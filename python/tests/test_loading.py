"""The package reads repository-root JSON and does not vendor a second copy."""

from __future__ import annotations

from indonesia_holidays import list_supported_years
from indonesia_holidays.loading import data_directory
from indonesia_holidays.years import is_year_file, year_from_file_name
from tests.support import repo_root


def test_source_checkout_reads_the_repository_data_directory() -> None:
    assert data_directory() == repo_root() / "data"
    assert sorted(path.name for path in data_directory().iterdir() if is_year_file(path.name)) == [
        "2026.json",
        "2027.json",
    ]
    assert list_supported_years() == (2026, 2027)


def test_year_files_are_not_copied_into_the_python_tree() -> None:
    python_root = repo_root() / "python"
    assert not (python_root / "data").exists()
    assert not (python_root / "src" / "indonesia_holidays" / "data").exists()


def test_year_file_names() -> None:
    assert is_year_file("2026.json") is True
    assert year_from_file_name("2027.json") == 2027
    assert is_year_file("2026.JSON") is False
    assert is_year_file("notes.json") is False
    assert is_year_file("202.json") is False
    assert is_year_file("20266.json") is False
    assert year_from_file_name("notes.json") is None
