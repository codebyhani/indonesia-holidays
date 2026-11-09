"""Paths that stay valid when pytest is launched from ``python/``."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return the repository root that holds both packages and ``data/``."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "src" / "index.ts").is_file() and (parent / "data" / "2026.json").is_file():
            return parent
    raise RuntimeError("Python tests must run from the indonesia-holidays repository checkout.")
