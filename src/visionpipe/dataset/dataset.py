import os
import shutil
from pathlib import Path

from tqdm import tqdm

from visionpipe.image.utils import rewrite_img
from visionpipe.video.utils import extract_video_frames


class Dataset:
    """
    Dataset folder structure:
    data_root/
    +-- raw/
        +-- 001.mp4
        +-- 002.jpg
    +-- interim/
        +-- images/
            +-- v{video_md5[:16]}/
                +-- video_md5[:16]_000.jpg
            +-- i{img_md5[:2]}/
                +-- img_md5[:16].jpg
    +-- processed/
    +-- metadata/
    """

    def __init__(self, root: str | Path) -> None:
        os.umask(0)

        self.root = Path(root)

        self.img_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        self.video_exts = {".mp4", ".avi", ".mov"}
        self.exts = self.img_exts | self.video_exts

        self.make_raw()
        self.make_interim()

    def make_raw(self) -> None:
        raw_files = [
            p for p in self.root.glob("*") if p.suffix.lower() in self.exts
        ]
        raw_dir = self.root / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        for p in raw_files:
            shutil.move(p, raw_dir)

        interim_dir = self.root / "interim"
        interim_dir.mkdir(parents=True, exist_ok=True)

    def make_interim(self) -> None:
        raw_files = sorted(
            [
                p
                for p in self.root.glob("raw/**/*")
                if p.suffix.lower() in self.exts
            ]
        )

        img_root = self.root / "interim" / "images"
        img_root.mkdir(parents=True, exist_ok=True)

        meta_dir = self.root / "metadata"
        meta_dir.mkdir(parents=True, exist_ok=True)

        for p in tqdm(raw_files, desc="Making interim dir...", disable=None):
            if p.suffix.lower() in self.video_exts:
                extract_video_frames(
                    p, save_root=img_root, md5_stem=True, meta_dir=meta_dir
                )
            else:
                rewrite_img(p, rewrite_root=img_root, meta_dir=meta_dir)
