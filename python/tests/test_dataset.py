"""The shipped 2026 and 2027 annexes, through the public functions."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from indonesia_holidays import (
    Holiday,
    InvalidOptionError,
    UnsupportedYearError,
    get_holiday,
    get_holidays,
    get_next_holiday,
    get_working_days,
    is_holiday,
    list_supported_years,
)
from indonesia_holidays.dates import civil_weekday, parse_civil_date
from tests.expected import EXPECTED_2026, EXPECTED_2027, WEEKDAY_NAMES, ExpectedHoliday


def test_ships_2026_and_2027_only() -> None:
    assert list_supported_years() == (2026, 2027)


@pytest.mark.parametrize(
    ("year", "expected", "national_count", "collective_count"),
    [
        (2026, EXPECTED_2026, 17, 8),
        (2027, EXPECTED_2027, 18, 8),
    ],
)
def test_matches_the_skb_annex(
    year: int,
    expected: tuple[ExpectedHoliday, ...],
    national_count: int,
    collective_count: int,
) -> None:
    holidays = get_holidays(year)
    assert tuple(_to_expected(holiday) for holiday in holidays) == expected
    assert len({holiday.date for holiday in holidays}) == len(holidays)
    assert len([holiday for holiday in holidays if holiday.type == "national_holiday"]) == (
        national_count
    )
    assert len([holiday for holiday in holidays if holiday.type == "collective_leave"]) == (
        collective_count
    )
    for holiday in holidays:
        assert isinstance(holiday.date, str)
        weekday = civil_weekday(parse_civil_date(holiday.date))
        printed = WEEKDAY_NAMES[weekday]
        row = next(item for item in expected if item.date == holiday.date)
        assert printed == row.weekday
        assert holiday.source.kind == "skb_3_menteri"
        assert not holiday.source.title.startswith("TEST FIXTURE")
        assert holiday.source.amendments == ()
        assert len(holiday.source.numbers) >= 3
        assert all(url.url.startswith("https://") for url in holiday.source.urls)
        assert holiday.date.startswith(f"{year}-")
        assert holiday.source.issued_on
        with pytest.raises(FrozenInstanceError):
            holiday.source.title = "changed"  # type: ignore[misc]


def test_keeps_cuti_bersama_out_of_the_default_results() -> None:
    assert is_holiday("2026-02-16") is False
    assert is_holiday("2026-02-16", include_collective_leave=True) is True
    assert is_holiday(date(2026, 2, 17)) is True
    collective = get_holiday("2026-02-16")
    assert collective is not None
    assert collective.type == "collective_leave"
    assert get_holiday(date(2026, 1, 2)) is None

    assert get_working_days("2026-01-01", "2026-01-31") == 20
    assert get_working_days(date(2026, 1, 1), date(2026, 1, 31)) == 20
    assert get_working_days("2026-02-01", "2026-02-28") == 19
    assert get_working_days("2026-02-01", "2026-02-28", include_collective_leave=True) == 18
    assert get_working_days("2026-01-01", "2026-01-01") == 0
    assert get_working_days("2026-01-02", "2026-01-02") == 1
    assert get_working_days("2026-01-03", "2026-01-03") == 0
    assert get_working_days("2026-12-31", "2027-01-01") == 1


def test_walks_forward_through_supported_years_and_stops_when_the_data_ends() -> None:
    assert _date_of(get_next_holiday("2025-12-31")) == "2026-01-01"
    assert _date_of(get_next_holiday(date(2026, 1, 1))) == "2026-01-16"
    assert _date_of(get_next_holiday("2026-01-01", inclusive=True)) == "2026-01-01"
    assert _date_of(get_next_holiday("2026-02-16")) == "2026-02-17"
    assert _date_of(get_next_holiday("2026-02-15", include_collective_leave=True)) == "2026-02-16"
    assert _date_of(get_next_holiday("2026-12-25")) == "2027-01-01"
    assert _date_of(get_next_holiday("2026-12-23", include_collective_leave=True)) == "2026-12-24"
    assert _date_of(get_next_holiday("2027-12-25")) == "2027-12-26"
    assert get_next_holiday("2027-12-26") is None
    assert get_next_holiday("2028-01-01") is None
    assert len(get_holidays(2026, ["national_holiday"])) == 17
    assert len(get_holidays(2027, ["collective_leave"])) == 8
    assert get_holidays(2026, []) == ()
    assert len(get_holidays(2026, ["national_holiday", "national_holiday"])) == 17


def test_can_treat_friday_and_saturday_as_the_weekend() -> None:
    assert get_working_days("2026-01-02", "2026-01-04", weekends=[5, 6]) == 1


def test_empty_weekends_count_only_holidays_as_blocked() -> None:
    assert get_working_days("2026-01-03", "2026-01-03", weekends=[]) == 1
    assert get_working_days("2026-01-01", "2026-01-01", weekends=[]) == 0


def test_rejects_a_range_that_leaves_the_shipped_years() -> None:
    with pytest.raises(UnsupportedYearError) as year_error:
        get_holidays(2025)
    assert year_error.value.year == 2025
    assert year_error.value.supported_years == (2026, 2027)
    with pytest.raises(UnsupportedYearError):
        get_holiday("2024-02-29")
    with pytest.raises(UnsupportedYearError):
        get_working_days("2027-12-31", "2028-01-02")
    with pytest.raises(InvalidOptionError):
        get_holidays("2026")  # type: ignore[arg-type]


def test_date_input_returns_string_records() -> None:
    holiday = get_holiday(date(2026, 8, 17))
    assert holiday is not None
    assert holiday.date == "2026-08-17"
    assert isinstance(holiday.date, str)
    assert holiday.name == "Proklamasi Kemerdekaan"
    listed = get_holidays(2026)
    assert holiday is next(item for item in listed if item.date == "2026-08-17")


def test_unknown_keyword_is_rejected() -> None:
    with pytest.raises(TypeError):
        is_holiday("2026-01-01", collective=True)  # type: ignore[call-arg]


def _to_expected(holiday: Holiday) -> ExpectedHoliday:
    weekday = WEEKDAY_NAMES[civil_weekday(parse_civil_date(holiday.date))]
    return ExpectedHoliday(
        date=holiday.date,
        name=holiday.name,
        type=holiday.type,
        weekday=weekday,
    )


def _date_of(holiday: Holiday | None) -> str:
    assert holiday is not None
    return holiday.date
