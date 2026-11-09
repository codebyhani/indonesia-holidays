"""Offline Indonesian national public holidays and collective leave.

Dates passed to these functions may be a ``datetime.date`` or a ``YYYY-MM-DD``
string. Records returned from the dataset keep ``YYYY-MM-DD`` strings, matching
``data/*.json`` and the TypeScript package.
"""

from __future__ import annotations

from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version

from indonesia_holidays.calendar import create_calendar
from indonesia_holidays.errors import (
    HolidayDataError,
    HolidayError,
    InvalidDateError,
    InvalidOptionError,
    InvalidRangeError,
    UnsupportedYearError,
)
from indonesia_holidays.loading import load_datasets
from indonesia_holidays.types import (
    Amendment,
    Holiday,
    HolidayType,
    OfficialSource,
    SourceKind,
    SourceNumber,
    SourceUrl,
    Weekday,
)

try:
    __version__ = version("indonesia-holidays")
except PackageNotFoundError:
    __version__ = "0.1.0"

_CALENDAR = create_calendar(load_datasets())


def list_supported_years() -> tuple[int, ...]:
    """Years shipped with this package, in ascending order.

    A year is listed only when its SKB 3 Menteri annex has been transcribed
    from a primary source into ``data/YYYY.json``.
    """
    return _CALENDAR.list_supported_years()


def get_holidays(
    year: int,
    types: Sequence[str] | None = None,
) -> tuple[Holiday, ...]:
    """Official records for one supported year, sorted by date.

    A national holiday is ordered before collective leave when both exist on
    the same date. Both types are returned unless ``types`` is set. An empty
    sequence returns no rows. Duplicate type names collapse.

    Raises:
        InvalidOptionError: ``year`` or ``types`` is not usable.
        UnsupportedYearError: this package has no dataset for ``year``.
    """
    return _CALENDAR.get_holidays(year, types)


def is_holiday(
    day: object,
    *,
    include_collective_leave: bool = False,
) -> bool:
    """Whether ``day`` is an official holiday.

    ``day`` is a ``datetime.date`` or a ``YYYY-MM-DD`` string. National holidays
    count by default. Cuti bersama counts only when ``include_collective_leave``
    is true. A supported year with no record on that date returns false.

    Raises:
        InvalidDateError: ``day`` is not a real civil date.
        InvalidOptionError: ``include_collective_leave`` is not a boolean.
        UnsupportedYearError: this package has no dataset for that year.
    """
    return _CALENDAR.is_holiday(
        day,
        include_collective_leave=include_collective_leave,
    )


def get_holiday(day: object) -> Holiday | None:
    """The official record for ``day``, or ``None`` when that year has no row.

    A national holiday is preferred when a date has both types. This does not
    apply the cuti-bersama inclusion flag used by :func:`is_holiday`. ``date``
    on the returned record is still a ``YYYY-MM-DD`` string.

    Raises:
        InvalidDateError: ``day`` is not a real civil date.
        UnsupportedYearError: this package has no dataset for that year.
    """
    return _CALENDAR.get_holiday(day)


def get_next_holiday(
    from_day: object,
    *,
    inclusive: bool = False,
    include_collective_leave: bool = False,
) -> Holiday | None:
    """The next official holiday on or after the day following ``from_day``.

    Pass ``inclusive=True`` to allow a holiday that falls on ``from_day``.
    Cuti bersama is skipped unless ``include_collective_leave`` is true.

    Returns ``None`` when no later matching record exists in the shipped
    datasets, including dates before the first supported year and dates after
    the last shipped holiday. It does not raise for an unsupported year.

    Raises:
        InvalidDateError: ``from_day`` is not a real civil date.
        InvalidOptionError: a flag is not a boolean.
    """
    return _CALENDAR.get_next_holiday(
        from_day,
        inclusive=inclusive,
        include_collective_leave=include_collective_leave,
    )


def get_working_days(
    start: object,
    end: object,
    *,
    weekends: Sequence[int] | None = None,
    include_collective_leave: bool = False,
) -> int:
    """Working days in the inclusive civil range from ``start`` through ``end``.

    A date counts when its weekday is outside ``weekends`` and it is not a
    national holiday. Cuti bersama is still a working day unless
    ``include_collective_leave`` is true. The default weekend is Saturday and
    Sunday (``6`` and ``0``). The same date on both ends returns ``1`` when
    that day is a working day and ``0`` when it is not. There is no upper
    bound other than the supported years covered by the range.

    Raises:
        InvalidDateError: either argument is not a real civil date.
        InvalidRangeError: ``start`` is after ``end``.
        InvalidOptionError: ``weekends`` or a flag is not usable.
        UnsupportedYearError: any year touched by the range has no dataset.
    """
    return _CALENDAR.get_working_days(
        start,
        end,
        weekends=weekends,
        include_collective_leave=include_collective_leave,
    )


__all__ = [
    "Amendment",
    "Holiday",
    "HolidayDataError",
    "HolidayError",
    "HolidayType",
    "InvalidDateError",
    "InvalidOptionError",
    "InvalidRangeError",
    "OfficialSource",
    "SourceKind",
    "SourceNumber",
    "SourceUrl",
    "UnsupportedYearError",
    "Weekday",
    "__version__",
    "get_holiday",
    "get_holidays",
    "get_next_holiday",
    "get_working_days",
    "is_holiday",
    "list_supported_years",
]
