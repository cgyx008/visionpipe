# visionpipe

[English](README.md) | 简体中文

一个小型、实用的 Python 计算机视觉工具集。

项目正在开发中，公共 API 保持精简，1.0 之前可能发生变化。

## 功能

- 从图片和视频目录整理数据集
- 不解码视频帧，直接读取视频元数据
- 抽取视频帧，并处理旋转方向
- 重写图片，并用 JSONL 记录元数据

## 环境要求

- Python 3.12 或更高版本（CI 在 Linux 和 Windows 上测试 3.12–3.15）
- 运行时依赖：NumPy、OpenCV、PyAV、tqdm

## 安装

```bash
pip install visionpipe
```

开发环境见下方 Development 一节。

## 快速开始

### 准备数据集

```python
import visionpipe as vp

vp.dataset.Dataset("data/root")
```

`Dataset` 会把 `data/root` 下的媒体文件移动到 `data/root/raw/`，然后原地处理。请只对准备重新整理的目录运行。

处理前：

```text
data/root/
├── still.jpg
└── video.mp4
```

处理后：

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

### 读取视频元数据

```python
import visionpipe as vp

meta = vp.video.get_video_meta("data/root/raw/video.mp4")
print(meta["width"], meta["height"], meta["fps"], meta["rotation"])
```

### 抽取视频帧

```python
import visionpipe as vp

vp.video.extract_video_frames(
    "data/root/raw/video.mp4",
    save_root="output/frames",
    meta_dir="output/meta",
    step_seconds=1,
)
```

## 公共 API

| 调用                            | 用途                   | 说明                                                          |
|---------------------------------|------------------------|---------------------------------------------------------------|
| `vp.dataset.Dataset`            | 从图片和视频整理数据集 | 将媒体移入 `raw/`；写入 `interim/images/` 和 `metadata.jsonl` |
| `vp.video.get_video_meta`       | 读取视频元数据         | `width` 和 `height` 是旋转后的尺寸                            |
| `vp.video.extract_video_frames` | 抽取采样视频帧         | 会旋转像素；输出 JPEG 不含 EXIF orientation                   |
| `vp.image.rewrite_img`          | 重写图片并记录元数据   | 写入 JSONL 和按内容寻址的图片                                 |
| `vp.file.append_jsonl`          | 追加 JSON 记录         | 自动创建父目录；跳过完全重复的记录                            |
| `vp.file.calc_hash`             | 计算文件哈希           | 默认 MD5；会读取完整文件                                      |

## 开发

首次安装，或者在修改依赖后，安装项目和开发工具：

```powershell
# --extra dev 表示安装 pyproject.toml 中 dev 依赖组里的工具
uv sync --extra dev
```

### Lint 与格式化

`ruff check` 默认只报告问题。加 `--fix` 才会自动修复规则支持的问题。

```powershell
# 1. 预览安全的 lint 修复，不写文件
uv run --extra dev ruff check --fix --diff .

# 2. 应用安全的 lint 修复，例如调整 import 顺序
uv run --extra dev ruff check --fix .

# 3. 确认没有剩余的 lint 问题
uv run --extra dev ruff check .
```

先应用 lint 修复，再格式化，让格式化器决定最终排版。

```powershell
# 1. 预览会修改哪些文件
#    --diff 只打印差异，不写文件
uv run --extra dev ruff format --diff .

# 2. 应用格式化
uv run --extra dev ruff format .

# 3. 检查格式
#    如果有文件需要格式化，--check 会返回非 0
uv run --extra dev ruff format --check .
```

Ruff 参数说明

| 参数      | 适用命令                    | 作用                               |
|-----------|-----------------------------|------------------------------------|
| `--fix`   | `ruff check`                | 应用安全修复并写入文件             |
| `--diff`  | `ruff check`、`ruff format` | 只显示改动，不写文件               |
| `--check` | `ruff format`               | 只检查，不修改；需要修改时返回非 0 |

### 类型检查与测试

这些是 lint、format 之后的最后检查，CI 也会运行同样的内容。

```powershell
# 静态类型检查
uv run --extra dev mypy

# 运行测试
uv run --extra dev pytest
```

检查包能否正常导入：

```powershell
python -c "import visionpipe; print(visionpipe.__version__)"
```

## 项目结构

```text
src/visionpipe/   包源码
tests/            自动化测试
pyproject.toml    打包和工具配置
```

## 许可证

MIT，详见 [LICENSE](LICENSE)。
