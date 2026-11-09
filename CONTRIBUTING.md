# Contributing

This library stays offline and only ships holiday dates that can be read from a primary Indonesian government source. Do not infer a future year from a religious calendar, a news summary alone, or the previous year's pattern.

## Local setup

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

Python 3.10 or newer is required for the package in `python/`. From the repository root:

```bash
python -m pip install -e "./python[dev]"
```

Then, from `python/`:

```bash
ruff check src tests hatch_build.py scripts
ruff format --check src tests hatch_build.py scripts
mypy
pytest
```

CI runs `pytest` again with `TZ=Pacific/Pago_Pago` and `TZ=Pacific/Kiritimati`.

## Add a year

1. Find the SKB 3 Menteri (Keputusan Bersama Menteri Agama, Menteri Ketenagakerjaan, dan Menteri PANRB) for that year, including any later amendment.
2. Read the annex from an official PDF or JDIH record. Keep the Indonesian names. Split a multi-day row such as `21–22 Maret` into one record per civil date.
3. Add `data/YYYY.json` at the repository root. Do not copy it under `python/`. Use `kind: "skb_3_menteri"`. Put the decree title, the three numbers, the issue date, the place, the signatories, the URLs you actually read, and `amendments`.
4. Leave `amendments` as `[]` only when you found no amending decree. When an amendment changes a date, add the amendment metadata and change the affected rows. Say what changed in `summary`. Do not silently replace the original list.
5. Import the new file from `src/index.ts`. Python loads every `data/YYYY.json` from that same directory; it does not need a second import. Extend `tests/expected.ts` and `python/tests/expected.py` with the date, the annex name, the type, and the weekday printed in the annex. Update `python/tests/test_loading.py` so the shipped year list includes the new file. The weekday check fails if a date is shifted.
6. Run the Node checks above, and the Python lint, typecheck, and `pytest` commands.

Labeled experiments belong in `tests/fixtures/` with `kind: "test_fixture"` and a title that starts with `TEST FIXTURE`. They must not be imported by `src/index.ts`.

## Rules that keep the dataset honest

- A missing year is unsupported. Do not add an empty file so that calls return "not a holiday."
- Cuti bersama and hari libur nasional stay separate. Do not mark collective leave as a national holiday.
- Regional holidays, company holidays, and school calendars are out of scope.
- Normalize obvious scan errors (a split letter, `Harl` for `Hari`) only when another official copy of the same decree confirms the word, and describe that normalization in `notes`.

## Code

Public behavior is documented in the README and in `python/README.md`. Keep date math on civil dates. Do not parse a date-only string with `new Date("YYYY-MM-DD")` or read the local weekday. The Python package accepts `datetime.date` or `YYYY-MM-DD` and rejects `datetime.datetime`. Returned records stay strings in both packages.

Runtime dependencies stay empty. Validation, tests, the build, and lint run from devDependencies.

## Reporting a wrong date

Open an issue with the decree URL and the annex row. A news article that disagrees with the annex is a lead, not a source. The annex, or an official amendment, is the source.
