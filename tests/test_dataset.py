import json
import shutil
from collections.abc import Callable
from pathlib import Path

import cv2
import numpy as np
import pytest

from visionpipe.dataset import Dataset


def test_dataset_moves_and_processes_files(
    tmp_path: Path,
    make_video: Callable[..., Path],
) -> None:
    dataset_root = tmp_path / "dataset"
    dataset_root.mkdir()

    video = make_video()
    shutil.move(str(video), dataset_root / "video.mp4")
    cv2.imwrite(
        str(dataset_root / "image.jpg"),
        np.zeros((20, 30, 3), dtype=np.uint8),
    )

    Dataset(dataset_root)

    assert (dataset_root / "raw" / "video.mp4").is_file()
    assert (dataset_root / "raw" / "image.jpg").is_file()

    images = list((dataset_root / "interim" / "images").rglob("*.jpg"))
    assert len(images) == 2

    meta_path = dataset_root / "metadata" / "metadata.jsonl"
    lines = meta_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert all(isinstance(json.loads(line), dict) for line in lines)
    assert (dataset_root / "processed").is_dir()


def test_dataset_moves_nested_media_when_raw_missing(
    tmp_path: Path,
    make_video: Callable[..., Path],
) -> None:
    dataset_root = tmp_path / "dataset"
    nested = dataset_root / "session" / "videos"
    nested.mkdir(parents=True)

    video = make_video()
    shutil.move(str(video), nested / "video.mp4")
    cv2.imwrite(
        str(nested / "still.jpg"),
        np.zeros((20, 30, 3), dtype=np.uint8),
    )

    Dataset(dataset_root)

    moved = dataset_root / "raw" / "session" / "videos"
    assert (moved / "video.mp4").is_file()
    assert (moved / "still.jpg").is_file()
    assert not (dataset_root / "session").exists()

    images = list((dataset_root / "interim" / "images").rglob("*.jpg"))
    assert len(images) == 2


def test_dataset_moves_nested_media_when_raw_exists(
    tmp_path: Path,
    make_video: Callable[..., Path],
) -> None:
    dataset_root = tmp_path / "dataset"
    (dataset_root / "raw").mkdir(parents=True)
    source = dataset_root / "youtube"
    source.mkdir()

    video = make_video()
    shutil.move(str(video), source / "001.mp4")

    Dataset(dataset_root)

    assert (dataset_root / "raw" / "youtube" / "001.mp4").is_file()
    assert not source.exists()


def test_dataset_keeps_non_media_files(
    tmp_path: Path,
    make_video: Callable[..., Path],
) -> None:
    dataset_root = tmp_path / "dataset"
    source = dataset_root / "youtube"
    source.mkdir(parents=True)

    video = make_video()
    shutil.move(str(video), source / "001.mp4")
    (source / "notes.txt").write_text("keep", encoding="utf-8")

    Dataset(dataset_root)

    assert (dataset_root / "raw" / "youtube" / "001.mp4").is_file()
    assert (source / "notes.txt").is_file()


def test_dataset_keeps_generated_dirs_when_raw_missing(
    tmp_path: Path,
) -> None:
    dataset_root = tmp_path / "dataset"
    metadata = dataset_root / "metadata"
    metadata.mkdir(parents=True)
    (metadata / "keep.txt").write_text("keep", encoding="utf-8")
    (dataset_root / "interim").mkdir()
    (dataset_root / "processed").mkdir()

    Dataset(dataset_root)

    assert (metadata / "keep.txt").is_file()
    assert (dataset_root / "raw").is_dir()
    assert (dataset_root / "interim").is_dir()
    assert (dataset_root / "processed").is_dir()
    assert not (dataset_root / "raw" / "metadata").exists()
    assert not (dataset_root / "raw" / "interim").exists()
    assert not (dataset_root / "raw" / "processed").exists()


def test_dataset_keeps_media_already_in_raw(
    tmp_path: Path,
    make_video: Callable[..., Path],
) -> None:
    dataset_root = tmp_path / "dataset"
    target = dataset_root / "raw" / "youtube" / "001.mp4"
    target.parent.mkdir(parents=True)
    shutil.move(str(make_video()), target)

    Dataset(dataset_root)

    assert target.is_file()
    assert not (dataset_root / "youtube").exists()
    images = list((dataset_root / "interim" / "images").rglob("*.jpg"))
    assert len(images) == 1


def test_dataset_refuses_to_overwrite_existing_raw_file(
    tmp_path: Path,
    make_video: Callable[..., Path],
) -> None:
    dataset_root = tmp_path / "dataset"
    target = dataset_root / "raw" / "youtube" / "001.mp4"
    target.parent.mkdir(parents=True)
    shutil.move(str(make_video()), target)

    source = dataset_root / "youtube"
    source.mkdir()
    shutil.move(str(make_video()), source / "001.mp4")

    with pytest.raises(FileExistsError) as exc_info:
        Dataset(dataset_root)

    message = str(exc_info.value)
    assert str(target) in message
    assert str(source / "001.mp4") in message


def test_dataset_records_processing_error_and_continues(
    tmp_path: Path,
    make_video: Callable[..., Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dataset_root = tmp_path / "dataset"
    dataset_root.mkdir()
    shutil.move(str(make_video()), dataset_root / "video.mp4")
    cv2.imwrite(
        str(dataset_root / "image.jpg"),
        np.zeros((20, 30, 3), dtype=np.uint8),
    )

    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("broken video")

    monkeypatch.setattr(
        "visionpipe.dataset.dataset.extract_video_frames",
        fail,
    )

    Dataset(dataset_root)

    problems = [
        json.loads(line)
        for line in (dataset_root / "metadata" / "problems.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert problems[0]["kind"] == "processing_error"
    assert problems[0]["error"] == "broken video"

    images = list((dataset_root / "interim" / "images").rglob("*.jpg"))
    assert len(images) == 1


def test_dataset_does_not_swallow_keyboard_interrupt(
    tmp_path: Path,
    make_video: Callable[..., Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dataset_root = tmp_path / "dataset"
    dataset_root.mkdir()
    shutil.move(str(make_video()), dataset_root / "video.mp4")

    def interrupt(*args: object, **kwargs: object) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(
        "visionpipe.dataset.dataset.extract_video_frames",
        interrupt,
    )

    with pytest.raises(KeyboardInterrupt):
        Dataset(dataset_root)
