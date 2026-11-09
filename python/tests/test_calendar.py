"""Fixture calendars: leap day, shared dates, and the same error cases as TypeScript."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError

import pytest

from indonesia_holidays.calendar import create_calendar
from indonesia_holidays.errors import (
    HolidayDataError,
    InvalidOptionError,
    InvalidRangeError,
    UnsupportedYearError,
)
from tests.support import repo_root

_FIXTURES = repo_root() / "tests" / "fixtures"


def _load(name: str) -> object:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


_LEAP_FILE = _load("leap-2024.json")
_DUPLICATE_DATE = _load("duplicate-date.json")
_DUPLICATE_TYPE = _load("duplicate-same-type.json")
_LEAP = create_calendar([_LEAP_FILE])
_DUPLICATES = create_calendar([_DUPLICATE_DATE])


def test_leap_fixture_keeps_29_february_without_treating_it_as_official_data() -> None:
    assert isinstance(_LEAP_FILE, dict)
    source = _LEAP_FILE["source"]
    assert isinstance(source, dict)
    assert str(source["title"]).startswith("TEST FIXTURE")
    holiday = _LEAP.get_holiday("2024-02-29")
    assert holiday is not None
    assert holiday.name == "Fixture leap day"
    assert holiday.type == "national_holiday"
    assert isinstance(holiday.date, str)
    assert _LEAP.is_holiday("2024-02-29") is True
    assert _LEAP.is_holiday("2024-03-01") is False
    assert _LEAP.is_holiday("2024-03-01", include_collective_leave=True) is True


def test_counts_working_days_across_the_leap_day() -> None:
    assert _LEAP.get_working_days("2024-02-28", "2024-03-03") == 2
    assert (
        _LEAP.get_working_days(
            "2024-02-28",
            "2024-03-03",
            include_collective_leave=True,
        )
        == 1
    )


def test_returns_the_national_holiday_when_both_types_share_a_date() -> None:
    holiday = _DUPLICATES.get_holiday("2031-01-01")
    assert holiday is not None
    assert holiday.name == "Fixture national holiday"
    assert holiday.type == "national_holiday"
    assert [item.type for item in _DUPLICATES.get_holidays(2031)] == [
        "national_holiday",
        "collective_leave",
    ]
    assert len(holiday.source.amendments) == 1
    assert holiday.source.amendments[0].issued_on == "2031-02-01"
    with pytest.raises(FrozenInstanceError):
        holiday.name = "changed"  # type: ignore[misc]


def test_rejects_two_records_of_the_same_type_on_one_date() -> None:
    with pytest.raises(HolidayDataError, match="2032-04-01"):
        create_calendar([_DUPLICATE_TYPE])


def test_does_not_treat_an_absent_year_as_a_year_without_holidays() -> None:
    with pytest.raises(UnsupportedYearError) as holidays_error:
        _LEAP.get_holidays(2025)
    assert holidays_error.value.year == 2025
    assert holidays_error.value.supported_years == (2024,)
    with pytest.raises(UnsupportedYearError):
        _LEAP.is_holiday("2025-01-01")
    with pytest.raises(UnsupportedYearError):
        _LEAP.get_holiday("2028-02-29")
    with pytest.raises(UnsupportedYearError):
        _LEAP.get_working_days("2024-02-28", "2025-01-01")


def test_returns_none_from_get_next_holiday_when_no_later_dataset_exists() -> None:
    assert _LEAP.get_next_holiday("2023-12-31") is not None
    assert _LEAP.get_next_holiday("2023-12-31").date == "2024-02-29"  # type: ignore[union-attr]
    assert _LEAP.get_next_holiday("2024-02-29") is None
    inclusive = _LEAP.get_next_holiday("2024-02-29", inclusive=True)
    assert inclusive is not None
    assert inclusive.date == "2024-02-29"
    with_leave = _LEAP.get_next_holiday("2024-02-28", include_collective_leave=True)
    assert with_leave is not None
    assert with_leave.date == "2024-02-29"
    assert _LEAP.get_next_holiday("2024-03-01") is None
    both = _LEAP.get_next_holiday(
        "2024-03-01",
        inclusive=True,
        include_collective_leave=True,
    )
    assert both is not None
    assert both.date == "2024-03-01"


def test_treats_both_ends_as_inclusive_and_rejects_a_reversed_range() -> None:
    assert _LEAP.get_working_days("2024-02-28", "2024-02-28") == 1
    assert _LEAP.get_working_days("2024-02-29", "2024-02-29") == 0
    assert _LEAP.get_working_days("2024-03-02", "2024-03-02") == 0
    with pytest.raises(
        InvalidRangeError,
        match="start_date 2024-03-02 is after end_date 2024-02-28",
    ):
        _LEAP.get_working_days("2024-03-02", "2024-02-28")


def test_honors_a_custom_weekend() -> None:
    assert _LEAP.get_working_days("2024-03-03", "2024-03-03", weekends=[5, 6]) == 1
    assert _LEAP.get_working_days("2024-03-01", "2024-03-01", weekends=[5, 6]) == 0
    assert _LEAP.get_working_days("2024-03-02", "2024-03-02", weekends=[5, 6]) == 0
    assert (
        _LEAP.get_working_days(
            "2024-02-28",
            "2024-03-03",
            weekends=[0, 1, 2, 3, 4, 5, 6],
        )
        == 0
    )
    assert _LEAP.get_working_days("2024-03-02", "2024-03-02", weekends=[]) == 1
    assert _LEAP.get_working_days("2024-03-03", "2024-03-03", weekends=[]) == 1


def test_rejects_invalid_options_and_duplicate_years() -> None:
    with pytest.raises(InvalidOptionError):
        _LEAP.get_holidays(2024.5)
    with pytest.raises(InvalidOptionError):
        _LEAP.get_holidays(True)
    with pytest.raises(InvalidOptionError, match="observance"):
        _LEAP.get_holidays(2024, ["observance"])
    with pytest.raises(InvalidOptionError):
        _LEAP.get_holidays(2024, "national_holiday")
    with pytest.raises(InvalidOptionError):
        _LEAP.is_holiday("2024-02-29", include_collective_leave="yes")
    with pytest.raises(InvalidOptionError):
        _LEAP.get_working_days("2024-02-28", "2024-02-28", weekends=[7])
    with pytest.raises(InvalidOptionError):
        _LEAP.get_working_days("2024-02-28", "2024-02-28", weekends=b"\x06")
    with pytest.raises(HolidayDataError, match="2024"):
        create_calendar([_LEAP_FILE, _LEAP_FILE])
    assert _LEAP.list_supported_years() == (2024,)


def test_duplicate_fixture_stays_labeled_as_a_fixture() -> None:
    assert isinstance(_DUPLICATE_TYPE, dict)
    source = _DUPLICATE_TYPE["source"]
    assert isinstance(source, dict)
    assert source["kind"] == "test_fixture"
    assert str(source["title"]).startswith("TEST FIXTURE")
