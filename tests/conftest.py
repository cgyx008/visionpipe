from collections.abc import Callable
from pathlib import Path

import av
import numpy as np
import pytest


@pytest.fixture
def make_video(tmp_path: Path) -> Callable[..., Path]:
    def _make_video(
        name: str = "video.mp4",
        *,
        width: int = 80,
        height: int = 60,
        rotation: int = 0,
        container_format: str | None = None,
        codec: str = "mpeg4",
    ) -> Path:
        path = tmp_path / name
        kwargs = {"format": container_format} if container_format else {}

        with av.open(str(path), mode="w", **kwargs) as container:
            stream = container.add_stream(codec, rate=30)
            stream.width = width
            stream.height = height
            stream.pix_fmt = "yuv420p"
            if rotation:
                stream.set_display_rotation(rotation)

            for _ in range(3):
                array = np.zeros((height, width, 3), dtype=np.uint8)
                frame = av.VideoFrame.from_ndarray(array, format="bgr24")
                for packet in stream.encode(frame):
                    container.mux(packet)

            for packet in stream.encode():
                container.mux(packet)

        return path

    return _make_video
