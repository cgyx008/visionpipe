import contextlib
import os
import shutil
from pathlib import Path

from tqdm import tqdm

from visionpipe.image.utils import rewrite_img
from visionpipe.video.utils import _record_problem, extract_video_frames


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
        self.gen_dirs = {"raw", "interim", "metadata", "processed"}

        self.make_raw()
        self.make_interim()
        self.make_processed()

    def make_raw(self) -> None:
        raw_dir = self.root / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)

        moves: list[tuple[Path, Path]] = []
        for p in self.root.glob("**/*.*"):
            if not p.is_file() or p.suffix.lower() not in self.exts:
                continue

            rel = p.relative_to(self.root)
            if rel.parts[0] in self.gen_dirs:
                continue

            dst = raw_dir / rel
            if dst.exists():
                raise FileExistsError(
                    f"destination already exists: {dst}; source: {p}"
                )
            moves.append((p, dst))

        for p, dst in moves:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(p, dst)

        for d, _, _ in self.root.walk(top_down=False):
            if d == self.root:
                continue
            if d.relative_to(self.root).parts[0] in self.gen_dirs:
                continue
            with contextlib.suppress(OSError):
                d.rmdir()  # 非空抛 OSError

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

        for p in tqdm(
            raw_files,
            desc="Making interim dir...",
            disable=None,
            smoothing=0,
        ):
            try:
                if p.suffix.lower() in self.video_exts:
                    extract_video_frames(
                        p,
                        save_root=img_root,
                        md5_stem=True,
                        meta_dir=meta_dir,
                        show_progress=False,
                    )
                else:
                    rewrite_img(p, rewrite_root=img_root, meta_dir=meta_dir)
            except KeyboardInterrupt:
                raise
            except Exception as exc:
                _record_problem(
                    meta_dir,
                    p,
                    "processing_error",
                    error_type=type(exc).__name__,
                    error=str(exc),
                )

    def make_processed(self) -> None:
        """Create the processed directory for future pipeline stages."""
        d = self.root / "processed"
        d.mkdir(parents=True, exist_ok=True)
