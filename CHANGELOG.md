# Changelog

English | [简体中文](CHANGELOG.zh-CN.md)

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial package scaffold with a `src` layout and typed marker.
- Public API for the `video`, `image`, `dataset`, and `file` subpackages.
- Video metadata extraction with rotation-aware dimensions.
- Video frame extraction with rotation handling and support for containers
  without a reported frame count.
- Image rewriting with content-addressed output paths.
- JSONL metadata helpers with parent-directory creation and duplicate
  suppression.
- Dataset preparation for moving raw media, extracting video frames, and
  rewriting images.
- English and Simplified Chinese README files.
- Unit and integration tests covering image handling, video metadata, frame
  extraction, dataset preparation, and file metadata.
- GitHub Actions CI across Python 3.12–3.15 on Linux and Windows, plus a PyPI
  Trusted Publishing workflow.

### Fixed

- Read all stream fields before closing the PyAV container, which is required
  by PyAV 19.
- Reject display rotations other than 0, 90, 180, and 270 degrees.
- Raise an error when OpenCV fails to write an image, instead of silently
  producing missing output files.
- Keep video metadata dimensions and extracted frame orientation consistent.
