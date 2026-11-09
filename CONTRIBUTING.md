# Contributing

This library stays offline and only ships holiday dates that can be read from a primary Indonesian government source. Do not infer a future year from a religious calendar, a news summary alone, or the previous year's pattern.

## Add a year

1. Find the SKB 3 Menteri (Keputusan Bersama Menteri Agama, Menteri Ketenagakerjaan, dan Menteri PANRB) for that year, including any later amendment.
2. Read the annex from an official PDF or JDIH record. Keep the Indonesian names. Split a multi-day row such as `21–22 Maret` into one record per civil date.
3. Add `data/YYYY.json`. Use `kind: "skb_3_menteri"`. Put the decree title, the three numbers, the issue date, the place, the signatories, the URLs you actually read, and `amendments`.
4. Leave `amendments` as `[]` only when you found no amending decree. When an amendment changes a date, add the amendment metadata and change the affected rows. Say what changed in `summary`. Do not silently replace the original list.
5. Extend `tests/expected.ts` with the date, the annex name, the type, and the weekday printed in the annex. The weekday check fails if a date is shifted.
6. Run `npm test`, `npm run typecheck`, and `npm run lint`.

Labeled experiments belong in `tests/fixtures/` with `kind: "test_fixture"` and a title that starts with `TEST FIXTURE`. They must not be imported by `src/index.ts`.

## Rules that keep the dataset honest

- A missing year is unsupported. Do not add an empty file so that calls return "not a holiday."
- Cuti bersama and hari libur nasional stay separate. Do not mark collective leave as a national holiday.
- Regional holidays, company holidays, and school calendars are out of scope.
- Normalize obvious scan errors (a split letter, `Harl` for `Hari`) only when another official copy of the same decree confirms the word, and describe that normalization in `notes`.

## Code

Public behavior is documented in the README. Keep date math on civil `YYYY-MM-DD` values. Do not parse a date-only string with `new Date("YYYY-MM-DD")` or read the local weekday.

Runtime dependencies stay empty. Validation, tests, the build, and lint run from devDependencies.

## Reporting a wrong date

Open an issue with the decree URL and the annex row. A news article that disagrees with the annex is a lead, not a source. The annex, or an official amendment, is the source.
