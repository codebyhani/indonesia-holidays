"""Structural checks for a year file. Messages match the TypeScript package."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import cast

from indonesia_holidays.dates import parse_civil_date
from indonesia_holidays.errors import HolidayDataError
from indonesia_holidays.types import (
    Amendment,
    Holiday,
    HolidayType,
    OfficialSource,
    SourceKind,
    SourceNumber,
    SourceUrl,
)

_YEAR_KEYS = ("year", "source", "holidays")
_SOURCE_KEYS = (
    "id",
    "title",
    "kind",
    "numbers",
    "issuedOn",
    "place",
    "signatories",
    "urls",
    "amendments",
    "notes",
)
_HOLIDAY_KEYS = ("date", "name", "type", "sourceId")
_NUMBER_KEYS = ("ministry", "number")
_URL_KEYS = ("label", "url")
_AMENDMENT_KEYS = ("id", "title", "issuedOn", "urls", "summary")
_HTTPS_URL = re.compile(r"^https://\S+$")


class ValidatedYear:
    """A year file after validation. Holidays still carry the shared source object."""

    def __init__(
        self,
        year: int,
        source: OfficialSource,
        holidays: tuple[Holiday, ...],
    ) -> None:
        self.year = year
        self.source = source
        self.holidays = holidays


def validate_year_file(value: object) -> ValidatedYear:
    """Validate one year file and attach its source onto every holiday row."""
    record = _expect_record(value, "Year file")
    _assert_exact_keys(record, _YEAR_KEYS, "Year file")

    year = _expect_integer(record["year"], "Year file year")
    if year < 1 or year > 9999:
        raise HolidayDataError(f"Year file year {year} is outside 1..9999.")

    source = _validate_source(record["source"])
    holidays_input = _expect_array(record["holidays"], "Year file holidays")
    seen: set[str] = set()
    holidays: list[Holiday] = []
    for index, entry in enumerate(holidays_input):
        holiday = _validate_holiday(entry, year, source, index)
        key = f"{holiday.date}:{holiday.type}"
        if key in seen:
            raise HolidayDataError(f"Duplicate {holiday.type} on {holiday.date} in {source.id}.")
        seen.add(key)
        holidays.append(holiday)

    return ValidatedYear(year, source, tuple(holidays))


def _validate_source(value: object) -> OfficialSource:
    record = _expect_record(value, "Source")
    _assert_exact_keys(record, _SOURCE_KEYS, "Source")

    source_id = _expect_non_empty_string(record["id"], "Source id")
    title = _expect_non_empty_string(record["title"], "Source title")
    kind = _expect_source_kind(record["kind"])
    if kind == "test_fixture" and not title.startswith("TEST FIXTURE"):
        raise HolidayDataError(
            f'Test fixture source {source_id} must use a title that starts with "TEST FIXTURE".'
        )
    if kind == "skb_3_menteri" and title.startswith("TEST FIXTURE"):
        raise HolidayDataError(f"Official source {source_id} is labeled as a test fixture.")

    numbers = tuple(
        _validate_number(entry, index)
        for index, entry in enumerate(_expect_array(record["numbers"], "Source numbers"))
    )
    if len(numbers) == 0:
        raise HolidayDataError(f"Source {source_id} needs at least one decree number.")

    issued_on = _expect_date_string(record["issuedOn"], "Source issuedOn")
    place = _expect_non_empty_string(record["place"], "Source place")
    signatories = _expect_string_list(record["signatories"], "Source signatories")
    if len(signatories) == 0:
        raise HolidayDataError(f"Source {source_id} needs at least one signatory.")

    urls = tuple(
        _validate_url(entry, f"Source url {index}")
        for index, entry in enumerate(_expect_array(record["urls"], "Source urls"))
    )
    if len(urls) == 0:
        raise HolidayDataError(f"Source {source_id} needs at least one URL.")

    amendments = tuple(
        _validate_amendment(entry, index)
        for index, entry in enumerate(_expect_array(record["amendments"], "Source amendments"))
    )
    notes = _expect_string_list(record["notes"], "Source notes")
    return OfficialSource(
        id=source_id,
        title=title,
        kind=kind,
        numbers=numbers,
        issued_on=issued_on,
        place=place,
        signatories=signatories,
        urls=urls,
        amendments=amendments,
        notes=notes,
    )


def _validate_holiday(
    value: object,
    year: int,
    source: OfficialSource,
    index: int,
) -> Holiday:
    label = f"Holiday {index} in {source.id}"
    record = _expect_record(value, label)
    _assert_exact_keys(record, _HOLIDAY_KEYS, label)

    holiday_date = _expect_date_string(record["date"], f"{label} date")
    parsed = parse_civil_date(holiday_date)
    if parsed.year != year:
        raise HolidayDataError(f"{holiday_date} is listed in the {year} dataset ({source.id}).")

    name = _expect_non_empty_string(record["name"], f"{label} name")
    holiday_type = _expect_holiday_type(record["type"], label)
    source_id = _expect_non_empty_string(record["sourceId"], f"{label} sourceId")
    if source_id != source.id:
        raise HolidayDataError(f"{label} sourceId {source_id} does not match source {source.id}.")
    return Holiday(date=holiday_date, name=name, type=holiday_type, source=source)


def _validate_number(value: object, index: int) -> SourceNumber:
    label = f"Source number {index}"
    record = _expect_record(value, label)
    _assert_exact_keys(record, _NUMBER_KEYS, label)
    return SourceNumber(
        ministry=_expect_non_empty_string(record["ministry"], f"{label} ministry"),
        number=_expect_non_empty_string(record["number"], f"{label} number"),
    )


def _validate_url(value: object, label: str) -> SourceUrl:
    record = _expect_record(value, label)
    _assert_exact_keys(record, _URL_KEYS, label)
    url_label = _expect_non_empty_string(record["label"], f"{label} label")
    url = _expect_non_empty_string(record["url"], f"{label} url")
    if _HTTPS_URL.fullmatch(url) is None:
        raise HolidayDataError(f"{label} must be an absolute https URL: {url}.")
    return SourceUrl(label=url_label, url=url)


def _validate_amendment(value: object, index: int) -> Amendment:
    label = f"Amendment {index}"
    record = _expect_record(value, label)
    _assert_exact_keys(record, _AMENDMENT_KEYS, label)
    urls = tuple(
        _validate_url(entry, f"{label} url {url_index}")
        for url_index, entry in enumerate(_expect_array(record["urls"], f"{label} urls"))
    )
    if len(urls) == 0:
        raise HolidayDataError(f"{label} needs at least one URL.")
    return Amendment(
        id=_expect_non_empty_string(record["id"], f"{label} id"),
        title=_expect_non_empty_string(record["title"], f"{label} title"),
        issued_on=_expect_date_string(record["issuedOn"], f"{label} issuedOn"),
        urls=urls,
        summary=_expect_non_empty_string(record["summary"], f"{label} summary"),
    )


def _expect_holiday_type(value: object, label: str) -> HolidayType:
    if value == "national_holiday":
        return "national_holiday"
    if value == "collective_leave":
        return "collective_leave"
    raise HolidayDataError(f'{label} type must be "national_holiday" or "collective_leave".')


def _expect_source_kind(value: object) -> SourceKind:
    if value == "skb_3_menteri":
        return "skb_3_menteri"
    if value == "test_fixture":
        return "test_fixture"
    raise HolidayDataError('Source kind must be "skb_3_menteri" or "test_fixture".')


def _expect_date_string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise HolidayDataError(f"{label} must be a YYYY-MM-DD string.")
    parse_civil_date(value)
    return value


def _expect_record(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise HolidayDataError(f"{label} must be an object.")
    # JSON objects are string-keyed. Cast so values stay ``object`` rather than ``Any``.
    items = cast(dict[object, object], value)
    record: dict[str, object] = {}
    for key, item in items.items():
        if not isinstance(key, str):
            raise HolidayDataError(f"{label} has unknown property {key!r}.")
        record[key] = item
    return record


def _expect_array(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise HolidayDataError(f"{label} must be an array.")
    return cast(list[object], value)


def _expect_non_empty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or value.strip() == "" or value != value.strip():
        raise HolidayDataError(
            f"{label} must be a non-empty string without surrounding whitespace."
        )
    return value


def _expect_string_list(value: object, label: str) -> tuple[str, ...]:
    return tuple(
        _expect_non_empty_string(entry, f"{label} {index}")
        for index, entry in enumerate(_expect_array(value, label))
    )


def _expect_integer(value: object, label: str) -> int:
    # ``bool`` is an ``int`` subclass. A JSON boolean is not a year.
    if type(value) is not int:
        raise HolidayDataError(f"{label} must be an integer.")
    return value


def _assert_exact_keys(
    record: Mapping[str, object],
    keys: tuple[str, ...],
    label: str,
) -> None:
    expected = set(keys)
    for key in record:
        if key not in expected:
            raise HolidayDataError(f'{label} has unknown property "{key}".')
    for key in keys:
        if key not in record:
            raise HolidayDataError(f'{label} is missing "{key}".')
