import json
import shutil
from collections.abc import Callable
from pathlib import Path

import cv2
import numpy as np

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
