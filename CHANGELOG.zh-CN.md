# 更新日志

[English](CHANGELOG.md) | 简体中文

本项目的重要变更记录在这里。格式遵循
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)，版本号遵循
[Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

## [0.1.0] - 2026-10-22

### 新增

- 初始项目脚手架，使用 `src` 布局并包含类型标记。
- 为 `video`、`image`、`dataset`、`file` 子包提供公共 API。
- 视频元数据读取，宽高按旋转后的方向返回。
- 视频抽帧，支持旋转处理，并支持容器未记录总帧数的视频。
- 图片重写，输出路径按内容哈希组织。
- JSONL 元数据工具，自动创建父目录并跳过完全重复的记录。
- Dataset 整理功能：移动原始媒体、抽取视频帧、重写图片。
- 英文和简体中文 README。
- 单元和集成测试，覆盖图片处理、视频元数据、抽帧、Dataset 整理和文件元数据。
- GitHub Actions CI（Python 3.12–3.15，Linux 和 Windows）和 PyPI Trusted Publishing 发布流程。

### 修复

- 在关闭 PyAV 容器前读取所有流字段，满足 PyAV 19 的要求。
- 拒绝 0、90、180、270 以外的显示旋转角度。
- OpenCV 写图片失败时抛出异常，而不是静默生成缺失文件。
- 保持视频元数据尺寸和抽帧后的图片方向一致。
