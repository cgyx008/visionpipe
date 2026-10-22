import math
import os
import struct
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import av
import cv2
import numpy as np
from tqdm import tqdm

from visionpipe.file.utils import append_jsonl, calc_hash


def rotation_from_display_matrix(matrix: bytes | None) -> int:
    """Read rotation from FFmpeg's display matrix side data.

    Args:
        matrix: FFmpeg's display matrix side data.

    Returns:
        Rotation in degrees, normalized to 0..359.

    """
    if matrix is None or len(matrix) != struct.calcsize("=9i"):
        return 0

    values = struct.unpack("=9i", matrix)

    # An all-zero top-left vector means the matrix is unusable.
    if values[0] == 0 and values[1] == 0:
        return 0

    degrees = -math.degrees(math.atan2(values[1], values[0]))
    return round(degrees) % 360


def get_video_meta(p: str | Path) -> dict[str, Any]:
    """Read basic video metadata without decoding frames.

    Args:
        p: Path to the video file.

    Returns:
        Parsed video metadata.

    Raises:
        ValueError: If the file contains no video stream.
    """
    p = Path(p)
    with av.open(p) as container:
        if not container.streams.video:
            raise ValueError(f"no video stream: {p}")

        stream = container.streams.video[0]

        matrix = stream.codec_context.coded_side_data.get("display_matrix")
        rotation = rotation_from_display_matrix(matrix)
        if rotation not in {0, 90, 180, 270}:
            raise ValueError(f"unsupported rotation: {rotation}")
        width = stream.width if rotation in {0, 180} else stream.height
        height = stream.height if rotation in {0, 180} else stream.width

        # Prefer the average frame rate. Some containers leave it as 0/0,
        # in which case FFmpeg's guessed rate is used as a fallback.
        fps: float | None = None
        for rate in (stream.average_rate, stream.guessed_rate):
            if rate.numerator > 0 and rate.denominator > 0:
                fps = float(rate)
                break

        frames = stream.frames or None
        codec = stream.codec_context.name

        # container.duration is expressed in av.time_base units,
        # which are microseconds (1 / 1_000_000 second).
        duration: float | None = None
        if container.duration is not None and container.duration > 0:
            duration = container.duration / av.time_base
        elif stream.duration is not None and stream.duration > 0:
            duration = float(stream.duration * stream.time_base)
        elif fps is not None and frames:
            duration = frames / fps

    return {
        "path": p.as_posix(),
        "width": width,
        "height": height,
        "md5": calc_hash(p),
        "fps": fps,
        "frames": frames,
        "duration": duration,
        "codec": codec,
        "rotation": rotation,
    }


def extract_video_frames(
    p: str | Path,
    save_root: str | Path | None = None,
    md5_stem: bool = False,
    step_seconds: float = 1,
    meta_dir: str | Path | None = None,
) -> None:
    os.umask(0)

    p = Path(p)
    save_root = p.parent if save_root is None else Path(save_root)
    save_root.mkdir(parents=True, exist_ok=True)

    meta_dir = p.parent if meta_dir is None else Path(meta_dir)
    meta_dir.mkdir(parents=True, exist_ok=True)
    metadata = get_video_meta(p)
    append_jsonl(meta_dir / "metadata.jsonl", metadata)

    if not metadata["md5"] or not metadata["fps"]:
        return None

    frames = metadata["frames"]
    fps = metadata["fps"]
    step = max(round(fps * step_seconds), 1)

    rotation = metadata["rotation"]

    stem = metadata["md5"][:16] if md5_stem else p.stem
    frame_dir = save_root / f"v{stem}"
    frame_dir.mkdir(parents=True, exist_ok=True)

    retry = 3
    for i in range(retry):
        try:
            with av.open(p) as container:
                stream = container.streams.video[0]
                n0s = len(str(frames)) if frames is not None else 6

                pb = tqdm(container.decode(stream), total=frames, disable=None)
                for j, frame in enumerate(pb):
                    if j % step != 0:
                        continue

                    frame_path = frame_dir / f"{stem}_{str(j).zfill(n0s)}.jpg"
                    if frame_path.exists():
                        continue

                    img = frame.to_ndarray(format="bgr24")
                    img = np.ascontiguousarray(np.rot90(img, k=rotation // 90))
                    ok = cv2.imwrite(frame_path.as_posix(), img)
                    if not ok:
                        raise OSError(f"failed to write image: {frame_path}")

            break

        except av.error.InvalidDataError as e:
            if i < retry - 1:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                print(f"{ts} - {p} raises: {e}. Retrying {i + 2} / {retry}")
                time.sleep(1)

    return None
