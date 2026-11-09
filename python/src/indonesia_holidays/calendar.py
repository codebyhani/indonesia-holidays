"""Holiday lookup. Behavior matches ``src/calendar.ts`` aside from date inputs."""

from __future__ import annotations

import json
from collections.abc import Sequence

from indonesia_holidays.dates import (
    add_civil_days,
    civil_date_to_string,
    civil_weekday,
    compare_civil_dates,
    parse_civil_date,
    years_in_range,
)
from indonesia_holidays.errors import (
    HolidayDataError,
    InvalidDateError,
    InvalidOptionError,
    InvalidRangeError,
    UnsupportedYearError,
)
from indonesia_holidays.types import Holiday, HolidayType, Weekday
from indonesia_holidays.validate import validate_year_file

_DEFAULT_WEEKENDS: tuple[Weekday, ...] = (6, 0)
_TYPE_ORDER: dict[HolidayType, int] = {
    "national_holiday": 0,
    "collective_leave": 1,
}


class HolidayCalendar:
    """An immutable calendar built from validated year files."""

    def __init__(self, datasets: object) -> None:
        if isinstance(datasets, (str, bytes)) or not isinstance(datasets, Sequence):
            raise HolidayDataError("Holiday datasets must be a list of year files.")

        by_year: dict[int, tuple[Holiday, ...]] = {}
        for dataset in datasets:
            validated = validate_year_file(dataset)
            if validated.year in by_year:
                raise HolidayDataError(f"More than one dataset was provided for {validated.year}.")
            holidays = tuple(sorted(validated.holidays, key=_holiday_sort_key))
            by_year[validated.year] = holidays

        supported_years = tuple(sorted(by_year))
        chronological = tuple(holiday for year in supported_years for holiday in by_year[year])
        grouped: dict[str, list[Holiday]] = {}
        for holiday in chronological:
            grouped.setdefault(holiday.date, []).append(holiday)

        self._by_year = by_year
        self._supported_years = supported_years
        self._chronological = chronological
        self._by_date = {key: tuple(rows) for key, rows in grouped.items()}

    def list_supported_years(self) -> tuple[int, ...]:
        """Years present in this calendar, ascending."""
        return self._supported_years

    def get_holidays(
        self,
        year: object,
        types: Sequence[str] | None = None,
    ) -> tuple[Holiday, ...]:
        """Records for one supported year, date order, national holiday first."""
        checked_year = _require_year_argument(year)
        selected = _resolve_types(types)
        rows = self._require_year(checked_year)
        return tuple(holiday for holiday in rows if holiday.type in selected)

    def is_holiday(
        self,
        day: object,
        *,
        include_collective_leave: object = False,
    ) -> bool:
        """Whether ``day`` is a national holiday, plus collective leave when asked."""
        civil = parse_civil_date(day)
        include = _require_bool(include_collective_leave, "include_collective_leave")
        rows = self._require_year(civil.year)
        text = civil_date_to_string(civil)
        return any(
            holiday.date == text and _matches_inclusion(holiday, include) for holiday in rows
        )

    def get_holiday(self, day: object) -> Holiday | None:
        """The record for ``day``, preferring a national holiday when both types exist."""
        civil = parse_civil_date(day)
        self._require_year(civil.year)
        matches = self._by_date.get(civil_date_to_string(civil), ())
        for holiday in matches:
            if holiday.type == "national_holiday":
                return holiday
        if len(matches) > 0:
            return matches[0]
        return None

    def get_next_holiday(
        self,
        from_day: object,
        *,
        inclusive: object = False,
        include_collective_leave: object = False,
    ) -> Holiday | None:
        """The next matching holiday after ``from_day``, or on that day when inclusive.

        An unsupported year is not an error. The scan only sees shipped rows.
        """
        civil = parse_civil_date(from_day)
        include_start = _require_bool(inclusive, "inclusive")
        include_leave = _require_bool(include_collective_leave, "include_collective_leave")
        if include_start:
            start = civil
        else:
            try:
                start = add_civil_days(civil, 1)
            except InvalidDateError:
                return None
        for holiday in self._chronological:
            # Zero-padded ``YYYY-MM-DD`` strings sort in civil order.
            if compare_civil_dates(parse_civil_date(holiday.date), start) < 0:
                continue
            if _matches_inclusion(holiday, include_leave):
                return holiday
        return None

    def get_working_days(
        self,
        start: object,
        end: object,
        *,
        weekends: object = None,
        include_collective_leave: object = False,
    ) -> int:
        """Inclusive count of days that are outside ``weekends`` and not blocked.

        A national holiday always blocks. Collective leave blocks only when
        ``include_collective_leave`` is true, because the decree leaves that
        day to each employer. The weekend is tested before the holiday list,
        so a holiday that already falls on a weekend does not reduce the count
        a second time and no substitute weekday is added.
        """
        start_civil = parse_civil_date(start)
        end_civil = parse_civil_date(end)
        if compare_civil_dates(start_civil, end_civil) > 0:
            start_text = civil_date_to_string(start_civil)
            end_text = civil_date_to_string(end_civil)
            raise InvalidRangeError(
                f"start_date {start_text} is after end_date {end_text}. "
                "Both dates are inclusive, so start_date must fall on or before end_date."
            )

        for year in years_in_range(start_civil, end_civil):
            if year not in self._by_year:
                raise UnsupportedYearError(year, self._supported_years)

        skipped = _resolve_weekends(weekends)
        include_leave = _require_bool(include_collective_leave, "include_collective_leave")
        count = 0
        cursor = start_civil
        while True:
            if civil_weekday(cursor) not in skipped:
                rows = self._by_date.get(civil_date_to_string(cursor), ())
                blocked = any(_matches_inclusion(holiday, include_leave) for holiday in rows)
                if not blocked:
                    count += 1
            if compare_civil_dates(cursor, end_civil) == 0:
                break
            cursor = add_civil_days(cursor, 1)
        return count

    def _require_year(self, year: int) -> tuple[Holiday, ...]:
        rows = self._by_year.get(year)
        if rows is None:
            raise UnsupportedYearError(year, self._supported_years)
        return rows


def create_calendar(datasets: object) -> HolidayCalendar:
    """Validate ``datasets`` and build a calendar. Used by tests and package import."""
    return HolidayCalendar(datasets)


def _matches_inclusion(holiday: Holiday, include_collective_leave: bool) -> bool:
    if holiday.type == "national_holiday":
        return True
    return include_collective_leave


def _holiday_sort_key(holiday: Holiday) -> tuple[str, int]:
    return (holiday.date, _TYPE_ORDER[holiday.type])


def _require_year_argument(year: object) -> int:
    if type(year) is not int or year < 1 or year > 9999:
        raise InvalidOptionError(f"Year must be an integer from 1 to 9999, received {year!r}.")
    return year


def _require_bool(value: object, name: str) -> bool:
    if type(value) is bool:
        return value
    raise InvalidOptionError(f"{name} must be a boolean.")


def _resolve_types(types: Sequence[str] | None) -> frozenset[HolidayType]:
    if types is None:
        return frozenset(("national_holiday", "collective_leave"))
    if isinstance(types, (str, bytes)) or not isinstance(types, Sequence):
        raise InvalidOptionError(
            'types must be a sequence of "national_holiday" and "collective_leave".'
        )
    selected: set[HolidayType] = set()
    for holiday_type in types:
        if holiday_type == "national_holiday":
            selected.add("national_holiday")
            continue
        if holiday_type == "collective_leave":
            selected.add("collective_leave")
            continue
        raise InvalidOptionError(
            "Unknown holiday type "
            f"{_describe_option(holiday_type)}. "
            'Use "national_holiday" or "collective_leave".'
        )
    return frozenset(selected)


def _resolve_weekends(weekends: object) -> frozenset[Weekday]:
    values: object = _DEFAULT_WEEKENDS if weekends is None else weekends
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise InvalidOptionError(
            "weekends must be a sequence of weekday numbers from 0 (Sunday) through 6 (Saturday)."
        )
    selected: set[Weekday] = set()
    for value in values:
        if type(value) is not int or value < 0 or value > 6:
            raise InvalidOptionError(
                f"Invalid weekend day {value!r}. Use 0 (Sunday) through 6 (Saturday)."
            )
        selected.add(_weekday_literal(value))
    return frozenset(selected)


def _weekday_literal(value: int) -> Weekday:
    if value == 0:
        return 0
    if value == 1:
        return 1
    if value == 2:
        return 2
    if value == 3:
        return 3
    if value == 4:
        return 4
    if value == 5:
        return 5
    if value == 6:
        return 6
    raise InvalidOptionError(f"Invalid weekend day {value!r}. Use 0 (Sunday) through 6 (Saturday).")


def _describe_option(value: object) -> str:
    try:
        return json.dumps(value, ensure_ascii=False)
    except TypeError:
        return repr(value)
