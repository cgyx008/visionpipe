import json
from collections.abc import Callable
from pathlib import Path

import cv2
import pytest

import visionpipe.video.utils as video_utils
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


def test_extract_video_frames_can_disable_progress(
    make_video: Callable[..., Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    video = make_video()

    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("tqdm should not be called")

    monkeypatch.setattr("visionpipe.video.utils.tqdm", fail)

    extract_video_frames(
        video,
        save_root=tmp_path / "frames",
        meta_dir=tmp_path / "meta",
        show_progress=False,
    )

    files = sorted((tmp_path / "frames").rglob("*.jpg"))
    assert len(files) == 1


def test_extract_video_frames_records_metadata_error(tmp_path: Path) -> None:
    video = tmp_path / "bad.mp4"
    video.write_bytes(b"not a video")

    extract_video_frames(
        video,
        save_root=tmp_path / "frames",
        meta_dir=tmp_path / "meta",
    )

    records = [
        json.loads(line)
        for line in (tmp_path / "meta" / "problems.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert records[0]["kind"] == "metadata_error"
    assert records[0]["path"] == video.as_posix()


def test_extract_video_frames_records_frame_count_mismatch(
    make_video: Callable[..., Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    video = make_video()
    real_get_video_meta = video_utils.get_video_meta

    def fake_get_video_meta(path: str | Path) -> dict[str, object]:
        meta = real_get_video_meta(path)
        meta["frames"] += 1
        return meta

    monkeypatch.setattr(video_utils, "get_video_meta", fake_get_video_meta)

    extract_video_frames(
        video,
        save_root=tmp_path / "frames",
        meta_dir=tmp_path / "meta",
        show_progress=False,
    )

    records = [
        json.loads(line)
        for line in (tmp_path / "meta" / "problems.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert records[0]["kind"] == "frame_count_mismatch"
    assert records[0]["frames_expected"] == 4
    assert records[0]["frames_decoded"] == 3
