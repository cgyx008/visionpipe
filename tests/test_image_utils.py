import json
from pathlib import Path

import cv2
import numpy as np

from visionpipe.image import rewrite_img


def test_rewrite_img_creates_metadata_and_image(tmp_path: Path) -> None:
    source = tmp_path / "source.jpg"
    cv2.imwrite(str(source), np.zeros((20, 30, 3), dtype=np.uint8))

    rewrite_root = tmp_path / "rewrite"
    meta_dir = tmp_path / "meta"
    rewrite_img(source, rewrite_root=rewrite_root, meta_dir=meta_dir)

    meta_path = meta_dir / "metadata.jsonl"
    assert meta_path.is_file()

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["width"] == 30
    assert meta["height"] == 20
    assert meta["md5"] is not None

    rewritten = rewrite_root / f"i{meta['md5'][:2]}" / f"{meta['md5'][:16]}.jpg"
    assert rewritten.is_file()
    assert cv2.imread(str(rewritten)).shape == (20, 30, 3)
