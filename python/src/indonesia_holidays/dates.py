"""Civil-date parsing and arithmetic that does not consult the local timezone."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from indonesia_holidays.errors import InvalidDateError
from indonesia_holidays.types import Weekday

# ``\d`` would also match Unicode digits. Year files and callers use ASCII.
_DATE_RE = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$")


@dataclass(frozen=True, slots=True)
class CivilDate:
    """A Gregorian calendar day with no time and no timezone."""

    year: int
    month: int
    day: int


def parse_civil_date(value: object) -> CivilDate:
    """Accept a ``datetime.date`` or a ``YYYY-MM-DD`` string.

    ``datetime.datetime`` is rejected even though it subclasses ``datetime.date``.
    A time component, aware or naive, would make the civil day depend on a
    timezone. The JSON files stay strings; this function only parses inputs.
    """
    if type(value) is date:
        return CivilDate(value.year, value.month, value.day)
    if isinstance(value, str):
        return _parse_date_string(value)
    raise InvalidDateError(
        f"Expected a datetime.date or a YYYY-MM-DD string, received {_describe_received(value)}."
    )


def civil_date_to_string(civil: CivilDate) -> str:
    """Format a civil date as ``YYYY-MM-DD``."""
    return f"{civil.year:04d}-{civil.month:02d}-{civil.day:02d}"


def civil_weekday(civil: CivilDate) -> Weekday:
    """Return the weekday, ``0`` for Sunday through ``6`` for Saturday.

    ``datetime.date.weekday`` numbers Monday as ``0``. The shift below matches
    the TypeScript package and does not read the process timezone.
    """
    weekday = (date(civil.year, civil.month, civil.day).weekday() + 1) % 7
    return _as_weekday(weekday)


def compare_civil_dates(left: CivilDate, right: CivilDate) -> int:
    """Return a negative, zero, or positive comparison of two civil dates."""
    if left.year != right.year:
        return left.year - right.year
    if left.month != right.month:
        return left.month - right.month
    return left.day - right.day


def add_civil_days(civil: CivilDate, days: int) -> CivilDate:
    """Move ``days`` on the Gregorian calendar.

    ``datetime.date`` arithmetic is timezone-free. Overflow past year 1 or
    year 9999 becomes ``InvalidDateError`` instead of an internal exception.
    """
    try:
        shifted = date(civil.year, civil.month, civil.day) + timedelta(days=days)
    except OverflowError as exc:
        raise InvalidDateError(
            f"Cannot move {civil_date_to_string(civil)} by {days} days within the civil calendar."
        ) from exc
    return CivilDate(shifted.year, shifted.month, shifted.day)


def years_in_range(start: CivilDate, end: CivilDate) -> tuple[int, ...]:
    """Inclusive civil years touched by a range. The caller has already ordered it."""
    return tuple(range(start.year, end.year + 1))


def _parse_date_string(value: str) -> CivilDate:
    match = _DATE_RE.fullmatch(value)
    if match is None:
        raise InvalidDateError(
            "Expected a datetime.date or a YYYY-MM-DD string, "
            f"received {_describe_received(value)}."
        )
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    if not _is_real_civil_date(year, month, day):
        raise InvalidDateError(f"{value} is not a real calendar date.")
    return CivilDate(year, month, day)


def _is_real_civil_date(year: int, month: int, day: int) -> bool:
    """Gregorian check, including century leap years. ``datetime.date`` rejects year 0."""
    if year < 1 or year > 9999 or month < 1 or month > 12 or day < 1 or day > 31:
        return False
    try:
        date(year, month, day)
    except ValueError:
        return False
    return True


def _as_weekday(value: int) -> Weekday:
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
    raise InvalidDateError(f"Weekday {value} is outside 0..6.")


def _describe_received(value: object) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        return "null"
    # datetime subclasses date. Callers must pass a date-only value.
    if isinstance(value, datetime):
        return "a datetime.datetime"
    return type(value).__name__
