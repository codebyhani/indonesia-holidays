# indonesia-holidays

Offline lookup of Indonesian national public holidays and collective leave, plus working-day counts, for Python 3.10 or newer.

The dates come from the joint ministerial decree annexes for 2026 and 2027. This package does not call a website, ship a database, or invent the next year. A year without a transcribed decree is unsupported.

Maintained by Hani. The license is MIT.

Also available for JavaScript and TypeScript on [npm](https://www.npmjs.com/package/indonesia-holidays). Project docs: [repository README](https://github.com/codebyhani/indonesia-holidays#readme).

## Install

Requires Python 3.10 or newer.

```bash
pip install indonesia-holidays
```

There are no runtime dependencies.

## Example

```python
from datetime import date
from indonesia_holidays import (
    get_holiday,
    get_holidays,
    get_next_holiday,
    get_working_days,
    is_holiday,
)

get_holidays(2026)
# 17 national holidays and 8 collective-leave days, date order

is_holiday(date(2026, 1, 1))
# True — New Year 2026

is_holiday("2026-02-16")
# False — collective leave is excluded unless you opt in

is_holiday("2026-02-16", include_collective_leave=True)
# True

get_holiday("2026-08-17")
# Proklamasi Kemerdekaan, type "national_holiday", plus the decree metadata
# holiday.date is the string "2026-08-17"

get_next_holiday("2026-01-01")
# 16 January 2026. The start date itself is not included.

get_working_days("2026-01-01", "2026-01-31")
# 20 — both ends count; weekends are Saturday and Sunday; collective leave still counts as a working day
```

## API

Pass a `datetime.date` or a `YYYY-MM-DD` string. `datetime.datetime` is rejected, including timezone-aware values, because a time would make the civil day depend on a zone. Weekday and day arithmetic use the Gregorian calendar date only.

Records keep `YYYY-MM-DD` strings. JSON field `issuedOn` is `issued_on` on the Python record. `Holiday`, `OfficialSource`, `Amendment`, `SourceNumber`, and `SourceUrl` are frozen dataclasses.

| Function | Behavior |
| --- | --- |
| `list_supported_years()` | `(2026, 2027)` today. |
| `get_holidays(year, types=None)` | Records for one supported year. `types` can limit the result to `"national_holiday"`, `"collective_leave"`, or both. The default is both. An empty list returns no rows. |
| `is_holiday(day, *, include_collective_leave=False)` | `True` for a national holiday. Collective leave counts only when `include_collective_leave` is true. |
| `get_holiday(day)` | The record, or `None`. A national holiday wins if a date carries both types. Collective leave is returned when it is the only record. |
| `get_next_holiday(from_day, *, inclusive=False, include_collective_leave=False)` | The next match after `from_day`. `inclusive=True` allows a holiday on `from_day`. Returns `None` when no later shipped record matches, including dates before 2026 and after the last 2027 holiday. |
| `get_working_days(start, end, *, weekends=None, include_collective_leave=False)` | Inclusive count of working days. |

`get_working_days` skips Saturday and Sunday by default (`6` and `0`). Pass `weekends` as weekday numbers, `0` for Sunday and `6` for Saturday, to use another weekend. An empty sequence disables the weekend, so only holidays block a day. A day is also skipped when it is a national holiday. It is skipped for collective leave only when `include_collective_leave` is true.

The same date on both ends returns `1` when that day is a working day and `0` when it is not. `start` after `end` raises.

### Errors

Every raised error extends `HolidayError`.

| Error | When |
| --- | --- |
| `InvalidDateError` | The value is not a `datetime.date` or a real `YYYY-MM-DD` date. A `datetime.date` is accepted. A `datetime.datetime` is rejected, as are `2026-02-29`, `2026-04-31`, and `2026/01/01`. `2024-02-29` is a real date, but this package still has no 2024 dataset. |
| `InvalidRangeError` | `start` is after `end`. |
| `InvalidOptionError` | The year, a holiday type, a weekend day, or a boolean flag is unusable. |
| `UnsupportedYearError` | `get_holidays`, `is_holiday`, `get_holiday`, or `get_working_days` touched a year that is not shipped. `error.year` and `error.supported_years` say which. Missing data is not reported as "not a holiday." |
| `HolidayDataError` | A year file failed its structural checks. Published data is validated when the module loads. |

`get_next_holiday` does not raise `UnsupportedYearError`. A date in 2025 can still see the 2026 New Year, and a date in 2028 returns `None`.

## Collective leave and employer policy

Collective leave is not a national public holiday.

The decree says collective leave reduces annual leave under the rules of each workplace, and that private institutions arrange it through their own leadership. This package therefore leaves collective leave out of `is_holiday`, `get_next_holiday`, and `get_working_days` until the caller sets `include_collective_leave=True`.

That flag is a calendar switch. It does not know an employment contract, a company policy, or whether someone was actually required to work.

`get_holiday("2026-02-16")` still returns the collective-leave record, so you can show the name without treating the day as a public holiday.

## Data

The holiday rows are `data/2026.json` and `data/2027.json` at the repository root. This package ships those files. A row has `date`, the official `name` printed in the annex, and `type` (`national_holiday` or `collective_leave`). Dates in the JSON and on returned records stay `YYYY-MM-DD` strings.

| Year | Instrument | Issued | National | Collective leave |
| --- | --- | --- | --- | --- |
| 2026 | Minister of Religious Affairs 1497/2025, Minister of Manpower 2/2025, Minister of Administrative and Bureaucratic Reform 5/2025 | 19 September 2025, Jakarta | 17 | 8 |
| 2027 | Minister of Religious Affairs 1205/2026, Minister of Manpower 3/2026, Minister of Administrative and Bureaucratic Reform 2/2026 | 15 September 2026, Jakarta | 18 | 8 |

Decree URLs and transcription notes are in the repository: [indonesia-holidays](https://github.com/codebyhani/indonesia-holidays#data).

## Limitations

- Only 2026 and 2027 are included. Later years wait for their own joint decree.
- There are no provincial or regency holidays.
- A caller must not treat `UnsupportedYearError` as proof that a date is a normal working day.
- If the Ministry of Religious Affairs revises an official crescent-sighting date after the joint decree, the dataset stays wrong until an official amendment is transcribed.
- Working-day counts ignore custom company closures except for the `weekends` and `include_collective_leave` switches.
