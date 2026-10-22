# visionpipe

English | [简体中文](README.zh-CN.md)

A small collection of practical computer-vision helpers for Python.

The package is under active development. Its public API is intentionally
small and may change before version 1.0.

## Features

- Prepare a dataset from a directory of images and videos
- Read video metadata without decoding frames
- Extract sampled frames from video with rotation handling
- Rewrite images and record metadata as JSONL

## Requirements

- Python 3.12 or newer (CI tests 3.12–3.15 on Linux and Windows)
- NumPy, OpenCV, PyAV, and tqdm are installed as runtime dependencies

## Installation

```bash
pip install visionpipe
```

For development, see the Development section below.

## Quick start

### Prepare a dataset

```python
import visionpipe as vp

vp.dataset.Dataset("data/root")
```

`Dataset` moves media files found directly under `data/root` into
`data/root/raw/`, then processes them in place. Run it on a directory you
intend to reorganize.

Before:

```text
data/root/
├── still.jpg
└── video.mp4
```

After:

```text
data/root/
├── raw/
│   ├── still.jpg
│   └── video.mp4
├── interim/
│   └── images/
│       ├── i<image-md5-prefix>/
│       │   └── <image-md5-prefix>.jpg
│       └── v<video-md5-prefix>/
│           └── <video-md5-prefix>_<frame>.jpg
└── metadata/
    └── metadata.jsonl
```

### Read video metadata

```python
import visionpipe as vp

meta = vp.video.get_video_meta("data/root/raw/video.mp4")
print(meta["width"], meta["height"], meta["fps"], meta["rotation"])
```

### Extract video frames

```python
import visionpipe as vp

vp.video.extract_video_frames(
    "data/root/raw/video.mp4",
    save_root="output/frames",
    meta_dir="output/meta",
    step_seconds=1,
)
```

## Public API

| Call                            | Purpose                                  | Notes                                                                  |
|---------------------------------|------------------------------------------|------------------------------------------------------------------------|
| `vp.dataset.Dataset`            | Prepare a dataset from images and videos | Moves media into `raw/`; writes `interim/images/` and `metadata.jsonl` |
| `vp.video.get_video_meta`       | Read video metadata                      | `width` and `height` are post-rotation                                 |
| `vp.video.extract_video_frames` | Extract sampled video frames             | Rotates pixels; output JPEGs have no EXIF orientation                  |
| `vp.image.rewrite_img`          | Rewrite an image and record its metadata | Writes JSONL metadata and a content-addressed image                    |
| `vp.file.append_jsonl`          | Append a JSON record                     | Creates parent directories; skips exact duplicates                     |
| `vp.file.calc_hash`             | Compute a file hash                      | MD5 by default; reads the full file                                    |

## Development

Install the project and its development tools once, or after changing
dependencies:

```powershell
# --extra dev installs the tools from [project.optional-dependencies].dev
uv sync --extra dev
```

### Linting and formatting

`ruff check` only reports problems by default. Add `--fix` to apply the
automatic fixes for rules that provide one.

```powershell
# 1. Preview safe lint fixes without writing files.
uv run --extra dev ruff check --fix --diff .

# 2. Apply safe lint fixes, such as import order.
uv run --extra dev ruff check --fix .

# 3. Verify that no lint issues remain.
uv run --extra dev ruff check .
```

Apply lint fixes before formatting, so the formatter has the final say on
layout.

```powershell
# 1. Preview which files would change.
#    --diff prints the changes without writing any files.
uv run --extra dev ruff format --diff .

# 2. Apply formatting.
uv run --extra dev ruff format .

# 3. Verify formatting.
#    --check fails if any file still needs formatting.
uv run --extra dev ruff format --check .
```

Ruff flag reference

| Flag      | Applies to                  | Meaning                                          |
|-----------|-----------------------------|--------------------------------------------------|
| `--fix`   | `ruff check`                | Apply safe fixes to files.                       |
| `--diff`  | `ruff check`, `ruff format` | Show changes without writing them.               |
| `--check` | `ruff format`               | Check only; exit non-zero if changes are needed. |


### Type checking and tests

These are the final checks after linting and formatting. CI runs the same
checks.

```powershell
# Static type checking.
uv run --extra dev mypy

# Run the test suite.
uv run --extra dev pytest
```

Check that the package imports:

```powershell
python -c "import visionpipe; print(visionpipe.__version__)"
```

## Layout

```text
src/visionpipe/   package source
tests/            automated tests
pyproject.toml    packaging and tool configuration
```

## License

MIT. See [LICENSE](LICENSE).
