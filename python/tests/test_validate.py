"""Year-file checks that are not covered by the shared fixtures."""

from __future__ import annotations

import pytest

from indonesia_holidays.calendar import create_calendar
from indonesia_holidays.errors import HolidayDataError


def _year(year: int = 2030) -> dict[str, object]:
    return {
        "year": year,
        "source": {
            "id": "fixture-min",
            "title": "TEST FIXTURE minimal",
            "kind": "test_fixture",
            "numbers": [{"ministry": "Test fixture", "number": "Not a decree"}],
            "issuedOn": f"{year:04d}-01-01",
            "place": "Fixture",
            "signatories": ["Test fixture"],
            "urls": [{"label": "Fixture", "url": "https://example.com/fixture"}],
            "amendments": [],
            "notes": ["Labeled test fixture."],
        },
        "holidays": [
            {
                "date": f"{year:04d}-01-02",
                "name": "Fixture day",
                "type": "national_holiday",
                "sourceId": "fixture-min",
            }
        ],
    }


def test_minimal_fixture_loads() -> None:
    calendar = create_calendar([_year()])
    holiday = calendar.get_holiday("2030-01-02")
    assert holiday is not None
    assert holiday.source.issued_on == "2030-01-01"
    assert holiday.source.kind == "test_fixture"


def test_rejects_unknown_and_missing_keys() -> None:
    extra = _year()
    extra["note"] = "no"
    with pytest.raises(HolidayDataError, match="unknown property"):
        create_calendar([extra])
    missing = _year()
    del missing["holidays"]
    with pytest.raises(HolidayDataError, match="missing"):
        create_calendar([missing])


def test_rejects_a_non_https_url_and_a_date_in_the_wrong_year() -> None:
    insecure = _year()
    source = insecure["source"]
    assert isinstance(source, dict)
    source["urls"] = [{"label": "Fixture", "url": "http://example.com/fixture"}]
    with pytest.raises(HolidayDataError, match="https"):
        create_calendar([insecure])

    wrong_year = _year()
    holidays = wrong_year["holidays"]
    assert isinstance(holidays, list)
    holidays[0]["date"] = "2031-01-02"
    with pytest.raises(HolidayDataError, match="2031-01-02"):
        create_calendar([wrong_year])


def test_rejects_mislabeled_fixture_and_official_titles() -> None:
    fixture = _year()
    source = fixture["source"]
    assert isinstance(source, dict)
    source["title"] = "not labeled"
    with pytest.raises(HolidayDataError, match="TEST FIXTURE"):
        create_calendar([fixture])

    official = _year()
    official_source = official["source"]
    assert isinstance(official_source, dict)
    official_source["kind"] = "skb_3_menteri"
    official_source["title"] = "TEST FIXTURE official"
    with pytest.raises(HolidayDataError, match="test fixture"):
        create_calendar([official])


def test_rejects_a_non_list_of_datasets() -> None:
    with pytest.raises(HolidayDataError, match="list of year files"):
        create_calendar({"year": 2030})
    with pytest.raises(HolidayDataError, match="list of year files"):
        create_calendar("[]")
