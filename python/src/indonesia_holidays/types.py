"""Public records. Date fields stay ``YYYY-MM-DD`` strings, matching the JSON."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

HolidayType = Literal["national_holiday", "collective_leave"]

# Sunday is 0 and Saturday is 6, matching the TypeScript weekday numbering.
Weekday = Literal[0, 1, 2, 3, 4, 5, 6]

SourceKind = Literal["skb_3_menteri", "test_fixture"]


@dataclass(frozen=True, slots=True)
class SourceNumber:
    """One ministry's decree number from a joint decision."""

    ministry: str
    number: str


@dataclass(frozen=True, slots=True)
class SourceUrl:
    """A labeled URL that was actually read for the decree."""

    label: str
    url: str


@dataclass(frozen=True, slots=True)
class Amendment:
    """A later decree that changes an earlier holiday decision.

    Production years keep this empty until an official amendment is verified.
    ``issued_on`` is the JSON ``issuedOn`` value, still a ``YYYY-MM-DD`` string.
    """

    id: str
    title: str
    issued_on: str
    urls: tuple[SourceUrl, ...]
    summary: str


@dataclass(frozen=True, slots=True)
class OfficialSource:
    """The decree metadata copied onto every holiday from that year file."""

    id: str
    title: str
    kind: SourceKind
    numbers: tuple[SourceNumber, ...]
    issued_on: str
    place: str
    signatories: tuple[str, ...]
    urls: tuple[SourceUrl, ...]
    amendments: tuple[Amendment, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Holiday:
    """One annex row.

    ``date`` stays a string. Callers may pass a ``datetime.date`` into the
    lookup functions, but the record itself matches the JSON and the
    TypeScript package.
    """

    date: str
    name: str
    type: HolidayType
    source: OfficialSource
