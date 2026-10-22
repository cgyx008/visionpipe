"""Practical computer-vision helpers for Python.

Subpackages are loaded lazily so importing :mod:`visionpipe` stays light.
"""

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from types import ModuleType

try:
    __version__ = version("visionpipe")
except PackageNotFoundError:  # pragma: no cover - source checkout fallback
    __version__ = "0.0.0"

_SUBMODULES = frozenset({"dataset", "file", "image", "video"})

__all__ = ["__version__"]


def __getattr__(name: str) -> ModuleType:
    """Import public subpackages on first access."""
    if name in _SUBMODULES:
        return import_module(f".{name}", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted({*globals(), *_SUBMODULES})
