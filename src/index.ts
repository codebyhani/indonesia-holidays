import { createCalendar } from "./calendar.js";
import type {
  GetHolidaysOptions,
  GetNextHolidayOptions,
  GetWorkingDaysOptions,
  Holiday,
  IsHolidayOptions,
} from "./types.js";
import year2026 from "../data/2026.json" with { type: "json" };
import year2027 from "../data/2027.json" with { type: "json" };

const calendar = createCalendar([year2026, year2027]);

export {
  HolidayDataError,
  HolidayError,
  InvalidDateError,
  InvalidOptionError,
  InvalidRangeError,
  UnsupportedYearError,
} from "./errors.js";

export type {
  Amendment,
  GetHolidaysOptions,
  GetNextHolidayOptions,
  GetWorkingDaysOptions,
  Holiday,
  HolidayType,
  IsHolidayOptions,
  OfficialSource,
  SourceKind,
  SourceNumber,
  SourceUrl,
  Weekday,
} from "./types.js";

/**
 * Years shipped with this package, in ascending order.
 * A year is listed only when its SKB 3 Menteri annex has been transcribed
 * from a primary source.
 */
export function listSupportedYears(): readonly number[] {
  return calendar.listSupportedYears();
}

/**
 * Official records for one supported year, sorted by date.
 * A national holiday is ordered before collective leave when both exist
 * on the same date. Both types are returned unless `types` is set.
 *
 * @throws {InvalidOptionError} `year` or `types` is not usable.
 * @throws {UnsupportedYearError} this package has no dataset for `year`.
 */
export function getHolidays(
  year: number,
  options?: GetHolidaysOptions,
): readonly Holiday[] {
  return calendar.getHolidays(year, options);
}

/**
 * Whether `date` is an official holiday.
 *
 * National holidays count by default. Cuti bersama counts only when
 * `includeCollectiveLeave` is `true`. A supported year with no record on
 * that date returns `false`.
 *
 * @throws {InvalidDateError} `date` is not a real `YYYY-MM-DD` civil date.
 * @throws {UnsupportedYearError} this package has no dataset for that year.
 */
export function isHoliday(date: string, options?: IsHolidayOptions): boolean {
  return calendar.isHoliday(date, options);
}

/**
 * The official record for `date`, or `null` when that supported year has
 * no record. A national holiday is preferred when a date has both types.
 * This does not apply the cuti-bersama inclusion flag used by `isHoliday`.
 *
 * @throws {InvalidDateError} `date` is not a real `YYYY-MM-DD` civil date.
 * @throws {UnsupportedYearError} this package has no dataset for that year.
 */
export function getHoliday(date: string): Holiday | null {
  return calendar.getHoliday(date);
}

/**
 * The next official holiday on or after the day following `fromDate`.
 * Pass `inclusive: true` to allow a holiday that falls on `fromDate`.
 * Cuti bersama is skipped unless `includeCollectiveLeave` is `true`.
 *
 * Returns `null` when no later matching record exists in the shipped
 * datasets, including dates before the first supported year and dates
 * after the last shipped holiday. It does not throw for an unsupported year.
 *
 * @throws {InvalidDateError} `fromDate` is not a real `YYYY-MM-DD` civil date.
 */
export function getNextHoliday(
  fromDate: string,
  options?: GetNextHolidayOptions,
): Holiday | null {
  return calendar.getNextHoliday(fromDate, options);
}

/**
 * Working days in the inclusive civil range from `startDate` through `endDate`.
 *
 * A date counts when its weekday is outside `weekends` and it is not a
 * national holiday. Cuti bersama is still a working day unless
 * `includeCollectiveLeave` is `true`. The default weekend is Saturday and
 * Sunday. The same date on both ends returns `1` when that day is a working
 * day and `0` when it is not. There is no upper bound other than the
 * supported years covered by the range.
 *
 * @throws {InvalidDateError} either argument is not a real `YYYY-MM-DD` date.
 * @throws {InvalidRangeError} `startDate` is after `endDate`.
 * @throws {UnsupportedYearError} any year touched by the range has no dataset.
 */
export function getWorkingDays(
  startDate: string,
  endDate: string,
  options?: GetWorkingDaysOptions,
): number {
  return calendar.getWorkingDays(startDate, endDate, options);
}
