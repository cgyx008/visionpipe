from pathlib import Path

import cv2

from visionpipe.file.utils import append_jsonl, calc_hash


def rewrite_img(
    p: str | Path,
    rewrite_root: str | Path | None = None,
    meta_dir: str | Path | None = None,
) -> None:
    """
    Rewrite the rotated image.
    """
    p = Path(p)
    img = cv2.imread(p.as_posix())
    if img is None:
        h, w, md5 = None, None, None
    else:
        h, w = img.shape[:2]
        md5 = calc_hash(p)

    meta = {"path": p.as_posix(), "width": w, "height": h, "md5": md5}
    meta_dir = p.parent if meta_dir is None else Path(meta_dir)
    append_jsonl(meta_dir / "metadata.jsonl", meta)

    if rewrite_root is None or img is None or md5 is None:
        return

    rewrite_root = Path(rewrite_root)
    rewrite_dir = rewrite_root / f"i{md5[:2]}"
    rewrite_dir.mkdir(parents=True, exist_ok=True)
    rewrite_path = rewrite_dir / f"{md5[:16]}.jpg"
    ok = cv2.imwrite(rewrite_path.as_posix(), img)
    if not ok:
        raise OSError(f"failed to write image: {rewrite_path}")
