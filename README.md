# indonesia-holidays

Offline lookup of Indonesian national public holidays and collective leave, plus working-day counts.

The dates come from the joint ministerial decree annexes for 2026 and 2027. The package does not call a website, ship a database, or invent the next year. A year without a transcribed decree is unsupported.

Maintained by Hani. This package is not on the npm registry yet. From a checkout of this repository:

```bash
npm ci
npm run build
node --input-type=module -e "import { getHolidays } from './dist/index.js'; console.log(getHolidays(2026).length)"
```

After it is published:

```bash
npm install indonesia-holidays
```

## Example

```ts
import {
  getHoliday,
  getHolidays,
  getNextHoliday,
  getWorkingDays,
  isHoliday,
} from "indonesia-holidays";

getHolidays(2026);
// 17 national holidays and 8 collective-leave days, date order

isHoliday("2026-01-01");
// true — New Year 2026

isHoliday("2026-02-16");
// false — collective leave is excluded unless you opt in

isHoliday("2026-02-16", { includeCollectiveLeave: true });
// true

getHoliday("2026-08-17");
// Independence Proclamation, type "national_holiday", plus the decree metadata

getNextHoliday("2026-01-01");
// 16 January 2026, the Prophet's Night Journey. The start date itself is not included.

getWorkingDays("2026-01-01", "2026-01-31");
// 20 — both ends count; weekends are Saturday and Sunday; collective leave still counts as a working day
```

## API

Dates are `YYYY-MM-DD` strings. They are civil dates, compared with UTC calendar fields so a local offset cannot move the day.

| Function | Behavior |
| --- | --- |
| `listSupportedYears()` | `[2026, 2027]` today. |
| `getHolidays(year, options?)` | Records for one supported year. `types` can limit the result to `"national_holiday"`, `"collective_leave"`, or both. The default is both. |
| `isHoliday(date, options?)` | `true` for a national holiday. Collective leave counts only when `includeCollectiveLeave` is `true`. |
| `getHoliday(date)` | The record, or `null`. A national holiday wins if a date ever carries both types. Collective leave is returned when it is the only record. |
| `getNextHoliday(fromDate, options?)` | The next match after `fromDate`. `inclusive: true` allows a holiday on `fromDate`. Returns `null` when no later shipped record matches, including dates before 2026 and after the last 2027 holiday. |
| `getWorkingDays(startDate, endDate, options?)` | Inclusive count of working days. |

`getWorkingDays` skips Saturday and Sunday by default. Pass `weekends` as weekday numbers, `0` for Sunday through `6` for Saturday, to use another weekend. A day is also skipped when it is a national holiday. It is skipped for collective leave only when `includeCollectiveLeave` is `true`.

The same date on both ends returns `1` when that day is a working day and `0` when it is not. `startDate` after `endDate` throws.

### Errors

Every thrown error extends `HolidayError`.

| Error | When |
| --- | --- |
| `InvalidDateError` | The string is not a real civil date. `2026-02-29`, `2026-04-31`, `2026/01/01`, and `Date` objects are rejected. `2024-02-29` is a real date, but this package still has no 2024 dataset. |
| `InvalidRangeError` | `startDate` is after `endDate`. |
| `InvalidOptionError` | The year, a holiday type, a weekend day, or a boolean flag is unusable. |
| `UnsupportedYearError` | `getHolidays`, `isHoliday`, `getHoliday`, or `getWorkingDays` touched a year that is not shipped. `error.year` and `error.supportedYears` say which. Missing data is not reported as "not a holiday." |
| `HolidayDataError` | A year file failed its structural checks. Published data is validated when the module loads. |

`getNextHoliday` does not throw `UnsupportedYearError`. A date in 2025 can still see the 2026 New Year, and a date in 2028 returns `null`.

## Collective leave and employer policy

Collective leave is not a national public holiday.

The decree says collective leave reduces annual leave under the rules of each workplace, and that private institutions arrange it through their own leadership. Vital public services (hospitals, utilities, transport, banks, and similar operations) are told to roster staff. This package therefore leaves collective leave out of `isHoliday`, `getNextHoliday`, and `getWorkingDays` until the caller sets `includeCollectiveLeave: true`.

That flag is a calendar switch. It does not know an employment contract, a company policy, or whether someone was actually required to work. It also does not calculate overtime or wage premiums.

`getHoliday("2026-02-16")` still returns the collective-leave record, so you can show the name without treating the day as a public holiday.

## Data

Each year lives in `data/YYYY.json`. A row has `date`, the official `name` printed in the annex, and `type` (`national_holiday` or `collective_leave`). The file's `source` object is copied onto every record the API returns: decree title, the three numbers, issue date, place, signatories, URLs, `amendments`, and notes.

| Year | Instrument | Issued | National | Collective leave |
| --- | --- | --- | --- | --- |
| 2026 | Minister of Religious Affairs 1497/2025, Minister of Manpower 2/2025, Minister of Administrative and Bureaucratic Reform 5/2025 | 19 September 2025, Jakarta | 17 | 8 |
| 2027 | Minister of Religious Affairs 1205/2026, Minister of Manpower 3/2026, Minister of Administrative and Bureaucratic Reform 2/2026 | 15 September 2026, Jakarta | 18 | 8 |

Primary text for 2026 was read from the [legal-documentation PDF](https://jdih.kemenkoinfra.go.id/dokumen/file/skb-libur-nasional-dan-cuti-bersama-tahun-2026.pdf). The [catalog record](https://jdih.kemenkoinfra.go.id/skb-liburnasional-cutibersama-tahun-2026) lists that decision as in force. The [State Secretariat announcement](https://www.setneg.go.id/baca/index/inilah_skb_3_menteri_libur_nasional_dan_cuti_bersama_2026) and the [Ministry of Manpower announcement](https://kemnaker.go.id/news/detail/pemerintah-umumkan-hari-libur-nasional-dan-cuti-bersama-2026-wamenaker-semoga-berjalan-lancar) match the annex.

Primary text for 2027 was read from both the [Ministry of Manpower PDF](https://jdih.kemnaker.go.id/asset/data_puu/2026skb003.pdf) and the [Coordinating Ministry for Infrastructure PDF](https://jdih.kemenkoinfra.go.id/dokumen/file/kepber/2026skb002.pdf). The [State Secretariat announcement](https://setneg.go.id/baca/index/inilah_skb_3_menteri_libur_nasional_dan_cuti_bersama_2027) and the [Ministry of Manpower announcement](https://kemnaker.go.id/news/detail/pemerintah-tetapkan-18-hari-libur-nasional-dan-8-hari-cuti-bersama-tahun-2027) match those annexes.

No holiday-date amendment was found for either year when the files were compiled on 9 November 2026. `amendments` is `[]`. Notes in each JSON file record the scan-to-text normalizations (collapsed whitespace, `Harl` stored as `Hari`, and `Hijirah` stored as `Hijriah` where the other official copy already uses that spelling).

The second clause of each decree says 1 Ramadan, Eid al-Fitr, and Eid al-Adha are set by a decree of the Minister of Religious Affairs. The annex already prints the Eid al-Fitr and Eid al-Adha dates stored here. 1 Ramadan is not a holiday in these decrees. This package does not calculate an Islamic calendar date.

## Limitations

- Only 2026 and 2027 are included. Later years wait for their own joint decree.
- There are no provincial or regency holidays.
- A caller must not treat `UnsupportedYearError` as proof that a date is a normal working day.
- If the Ministry of Religious Affairs revises an official crescent-sighting date after the joint decree, this file stays wrong until an official amendment is transcribed.
- Working-day counts ignore custom company closures except for the `weekends` and `includeCollectiveLeave` switches.

## Development

Requires Node.js 20 or newer. CI runs the same checks on Node 20 and 22.

```bash
npm ci
npm test
npm run typecheck
npm run lint
npm run build
```

`npm test` runs the suite in UTC and again in `Pacific/Pago_Pago` and `Pacific/Kiritimati`, so a date-only value cannot pass by accident of the machine timezone.

There are no runtime dependencies. Vitest, TypeScript, tsup, and ESLint are devDependencies.

See [CONTRIBUTING.md](CONTRIBUTING.md) for dataset updates and [MAINTAINERS.md](MAINTAINERS.md) for releases. The license is MIT.
