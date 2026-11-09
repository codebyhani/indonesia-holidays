# Maintainer notes

Code by Hani maintains this package. The public API is stable for 0.1.x: adding a year is a minor change, and changing a shipped date is a patch only when an official amendment requires it. Say so in the changelog note you add with that release.

## Versioning

npm and PyPI versions are independent. Bump and release only the package that changed. A shared dataset change usually means a release for both, each with its own next version.

## Before an npm release

1. Re-read the SKB annex PDFs linked from `data/YYYY.json`. Confirm `amendments` is still complete.
2. Run `npm run lint`, `npm run typecheck`, `npm test`, and `npm run build`.
3. Run `npm pack --dry-run`. The tarball should contain `dist/`, `data/2026.json`, `data/2027.json`, `README.md`, `LICENSE`, `CONTRIBUTING.md`, and `MAINTAINERS.md`. It should not contain `tests/` or `src/`.
4. Check the export map. `types` points at `dist/index.d.ts`, `import` at `dist/index.js`, and `require` at `dist/index.cjs`.
5. Bump `package.json` `version` on `main` only when you intend to publish.
6. Create a published GitHub release whose tag is `v` plus that version, for example `v0.1.1` for `0.1.1`. Title it like `Indonesia Holidays v0.1.1`. The `Publish to npm` workflow then publishes with trusted publishing.

Do not commit long-lived npm tokens. Trusted publishing is configured on the package settings page for `indonesia-holidays`, with workflow filename `publish.yml`.

## Before a PyPI release

1. Re-read the SKB annex PDFs linked from `data/YYYY.json`. Confirm `amendments` is still complete.
2. In `python/`, run the lint, typecheck, test, and build checks from `CONTRIBUTING.md`.
3. Bump `python/pyproject.toml` `version` on `main` only when you intend to publish.
4. Create a published GitHub release whose tag is `python-v` plus that version, for example `python-v0.1.1` for `0.1.1`. Title it like `Indonesia Holidays (Python) v0.1.1`. The `Publish to PyPI` workflow then publishes with trusted publishing.

Do not commit long-lived PyPI tokens. Trusted publishing is configured for project `indonesia-holidays`, with workflow filename `publish-python.yml`.

## When a decree changes

Record the new instrument in `amendments` with its URL, issue date, and a short summary of the date changes. Update the holiday rows and `tests/expected.ts` in the same change. Keep the original decree numbers on the source so a reader can see what was amended.

If the new instrument replaces the year's decision entirely, keep the old source identifiable in `notes` or as the amendment's summary. Do not drop the previous URL.

## What this package will not do

Do not add a network fetch, a database, or a generated calendar for years without an SKB. Do not calculate Idulfitri, Iduladha, or 1 Ramadan. The decree already says those dates are set by Keputusan Menteri Agama, and the annex is the list this package copies.

Cuti bersama stays opt-in for `isHoliday`, `getNextHoliday`, and `getWorkingDays`. Changing that default would treat an employer-specific leave day as a public holiday.

## Support window

`listSupportedYears()` is the contract for coverage. Callers who need a year that is not listed should catch `UnsupportedYearError` and wait for a dataset update. Do not advise them to treat the error as an ordinary working day without saying that holiday data is missing.
