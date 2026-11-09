"""Locate the shared year files without copying them into this package tree."""

from __future__ import annotations

import json
from pathlib import Path

from indonesia_holidays.errors import HolidayDataError
from indonesia_holidays.years import is_year_file


def data_directory() -> Path:
    """Return the directory that holds ``YYYY.json``.

    An installed wheel carries the files in ``indonesia_holidays/data`` because
    the build packs them there. A source checkout has no copy under ``python/``;
    the files stay at the repository root, next to the TypeScript package.
    """
    packaged = Path(__file__).resolve().parent / "data"
    if packaged.is_dir():
        return packaged
    repo_data = _source_checkout_data()
    if repo_data is not None:
        return repo_data
    raise HolidayDataError(
        "Holiday dataset was not found. Expected data/YYYY.json inside the "
        "installed package or at the repository root next to the TypeScript package."
    )


def load_datasets() -> list[object]:
    """Read every ``data/YYYY.json`` from :func:`data_directory` in year order."""
    directory = data_directory()
    paths = sorted(
        path for path in directory.iterdir() if path.is_file() and is_year_file(path.name)
    )
    if not paths:
        raise HolidayDataError(f"No holiday year files were found in {directory}.")
    return [_read_json(path) for path in paths]


def _source_checkout_data() -> Path | None:
    """Find ``<repo>/data`` when this module is running from ``python/src``.

    ``parents`` from ``python/src/indonesia_holidays/loading.py``:
    the package directory, ``src``, ``python``, then the repository root.
    The ``pyproject.toml`` check keeps an installed copy from walking into
    an unrelated directory that happens to contain a ``data`` folder.
    """
    here = Path(__file__).resolve()
    if len(here.parents) < 4:
        return None
    python_root = here.parents[2]
    repo_root = here.parents[3]
    repo_data = repo_root / "data"
    if (python_root / "pyproject.toml").is_file() and repo_data.is_dir():
        return repo_data
    return None


def _read_json(path: Path) -> object:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError as exc:
        raise HolidayDataError(f"{path.name} is not UTF-8.") from exc
    except OSError as exc:
        raise HolidayDataError(f"Could not read {path.name}.") from exc
    try:
        parsed: object = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HolidayDataError(f"{path.name} is not valid JSON.") from exc
    return parsed
