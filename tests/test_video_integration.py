from collections.abc import Callable
from pathlib import Path

import cv2
import pytest

from visionpipe.video import extract_video_frames, get_video_meta


def test_get_video_meta(make_video: Callable[..., Path]) -> None:
    video = make_video()

    meta = get_video_meta(video)

    assert meta["width"] == 80
    assert meta["height"] == 60
    assert meta["rotation"] == 0
    assert meta["frames"] == 3
    assert meta["fps"] == pytest.approx(30.0)
    assert meta["codec"] == "mpeg4"


def test_get_video_meta_applies_rotation(
    make_video: Callable[..., Path],
) -> None:
    video = make_video(rotation=90)

    meta = get_video_meta(video)

    assert meta["rotation"] == 90
    assert meta["width"] == 60
    assert meta["height"] == 80


def test_extract_video_frames_rotates_pixels(
    make_video: Callable[..., Path],
    tmp_path: Path,
) -> None:
    video = make_video(rotation=90)

    extract_video_frames(
        video,
        save_root=tmp_path / "frames",
        meta_dir=tmp_path / "meta",
        step_seconds=1,
    )

    files = sorted((tmp_path / "frames").rglob("*.jpg"))
    assert len(files) == 1

    image = cv2.imread(str(files[0]))
    assert image.shape == (80, 60, 3)


def test_extract_video_frames_with_unknown_frame_count(
    make_video: Callable[..., Path],
    tmp_path: Path,
) -> None:
    video = make_video(
        "stream.mkv",
        container_format="matroska",
    )
    meta = get_video_meta(video)
    assert meta["frames"] is None

    extract_video_frames(
        video,
        save_root=tmp_path / "frames",
        meta_dir=tmp_path / "meta",
        step_seconds=1,
    )

    files = sorted((tmp_path / "frames").rglob("*.jpg"))
    assert len(files) >= 1
