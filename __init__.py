"""Alethic — a governed cognition framework for AI systems."""
from importlib.metadata import PackageNotFoundError, version as _version

try:
    __version__ = _version("alethic-kernel")
except PackageNotFoundError:  # running from a source tree, not installed
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
