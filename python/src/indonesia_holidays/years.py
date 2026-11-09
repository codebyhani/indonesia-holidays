"""Year-file names shared by the loader and the wheel build.

The holiday dataset is the repository-root ``data/YYYY.json`` files.
This module only names those files. It does not copy them.
"""

from __future__ import annotations

import re

# Four-digit year and a lowercase ``.json`` extension, for example ``2026.json``.
YEAR_FILE_NAME = re.compile(r"^([0-9]{4})\.json$")


def is_year_file(name: str) -> bool:
    """Return whether ``name`` is a holiday year file, not a note or backup."""
    return YEAR_FILE_NAME.fullmatch(name) is not None


def year_from_file_name(name: str) -> int | None:
    """Return the year encoded in ``name``, or ``None`` when it is not a year file."""
    match = YEAR_FILE_NAME.fullmatch(name)
    if match is None:
        return None
    return int(match.group(1))
