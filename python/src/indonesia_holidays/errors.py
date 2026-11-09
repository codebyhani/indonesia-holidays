"""Errors raised by the public holiday API and by dataset validation."""

from __future__ import annotations

from collections.abc import Sequence


class HolidayError(Exception):
    """Base class for every error this package raises on purpose."""


class InvalidDateError(HolidayError):
    """The value is not a ``datetime.date`` or a real ``YYYY-MM-DD`` civil date."""


class InvalidRangeError(HolidayError):
    """``start`` is after ``end``. Both ends of a working-day range are inclusive."""


class UnsupportedYearError(HolidayError):
    """The requested year has no dataset.

    This is raised instead of treating the year as a year without holidays.
    ``get_next_holiday`` does not raise it: a date outside the shipped years
    can still see a later shipped holiday, or ``None`` when nothing remains.
    """

    def __init__(self, year: int, supported_years: Sequence[int]) -> None:
        self.year = year
        self.supported_years = tuple(supported_years)
        available = ", ".join(str(item) for item in self.supported_years) or "(none)"
        super().__init__(
            f"No official holiday dataset is available for {year}. Supported years: {available}."
        )


class InvalidOptionError(HolidayError):
    """An option has the wrong type or an unsupported value."""


class HolidayDataError(HolidayError):
    """A year file or fixture failed structural checks."""
