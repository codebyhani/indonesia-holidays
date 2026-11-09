"""Civil-date rules, including values the TypeScript package rejects or accepts."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from indonesia_holidays.dates import add_civil_days, civil_weekday, parse_civil_date
from indonesia_holidays.errors import InvalidDateError


def sakamoto_weekday(year: int, month: int, day: int) -> int:
    """Independent Gregorian weekday, 0 = Sunday. Does not use ``datetime``."""
    offsets = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)
    adjusted_year = year - 1 if month < 3 else year
    return (
        adjusted_year
        + adjusted_year // 4
        - adjusted_year // 100
        + adjusted_year // 400
        + offsets[month - 1]
        + day
    ) % 7


def test_accepts_leap_day_in_2024_and_2000_and_rejects_it_in_2026_and_1900() -> None:
    assert parse_civil_date("2024-02-29") == parse_civil_date(date(2024, 2, 29))
    assert parse_civil_date("2000-02-29").year == 2000
    with pytest.raises(InvalidDateError, match="not a real calendar date"):
        parse_civil_date("2026-02-29")
    with pytest.raises(InvalidDateError, match="not a real calendar date"):
        parse_civil_date("1900-02-29")


def test_rejects_dates_that_are_not_real_calendar_days() -> None:
    for value in (
        "2026-04-31",
        "2026-00-10",
        "2026-01-00",
        "2026-13-01",
        "",
        "2026/01/01",
        "2026-1-01",
        " 2026-01-01",
        "2026-01-01 ",
        "2026-01-01T00:00:00",
    ):
        with pytest.raises(InvalidDateError):
            parse_civil_date(value)


def test_rejects_datetime_and_other_non_dates() -> None:
    with pytest.raises(InvalidDateError, match=r"datetime\.datetime"):
        parse_civil_date(datetime(2026, 1, 1, tzinfo=timezone.utc))
    with pytest.raises(InvalidDateError, match=r"datetime\.datetime"):
        parse_civil_date(datetime(2026, 1, 1, 0, 0))
    with pytest.raises(InvalidDateError, match="null"):
        parse_civil_date(None)
    with pytest.raises(InvalidDateError, match="int"):
        parse_civil_date(20260101)


def test_accepts_year_1_as_a_real_civil_date() -> None:
    # datetime.date supports year 1. A missing dataset still fails later as unsupported.
    assert parse_civil_date("0001-01-01") == parse_civil_date(date(1, 1, 1))


def test_matches_an_independent_weekday_formula() -> None:
    samples = (
        "2026-01-01",
        "2024-02-28",
        "2024-02-29",
        "2024-03-01",
        "2026-12-31",
        "2027-01-01",
        "1900-03-01",
        "2000-02-29",
    )
    for value in samples:
        parsed = parse_civil_date(value)
        assert civil_weekday(parsed) == sakamoto_weekday(parsed.year, parsed.month, parsed.day)


def test_adds_days_across_month_and_leap_year_boundaries() -> None:
    assert add_civil_days(parse_civil_date("2024-02-28"), 1) == parse_civil_date("2024-02-29")
    assert add_civil_days(parse_civil_date("2026-02-28"), 1) == parse_civil_date("2026-03-01")
    assert add_civil_days(parse_civil_date("2026-12-31"), 1) == parse_civil_date("2027-01-01")
