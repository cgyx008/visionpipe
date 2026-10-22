import struct

import pytest

from visionpipe.video.utils import rotation_from_display_matrix

SCALE = 1 << 16


def make_display_matrix(cos: int, sin: int) -> bytes:
    """Create a 3x3 display matrix in FFmpeg's int32 layout."""
    return struct.pack(
        "=9i",
        cos * SCALE,
        sin * SCALE,
        0,
        -sin * SCALE,
        cos * SCALE,
        0,
        0,
        0,
        SCALE,
    )


@pytest.mark.parametrize(
    ("cos", "sin", "expected"),
    [
        (1, 0, 0),
        (0, -1, 90),
        (-1, 0, 180),
        (0, 1, 270),
    ],
)
def test_rotation_from_display_matrix(
    cos: int,
    sin: int,
    expected: int,
) -> None:
    matrix = make_display_matrix(cos, sin)

    assert rotation_from_display_matrix(matrix) == expected


def test_rotation_from_invalid_matrix() -> None:
    assert rotation_from_display_matrix(None) == 0
    assert rotation_from_display_matrix(b"\x00" * 8) == 0
    assert rotation_from_display_matrix(b"\x00" * 36) == 0
