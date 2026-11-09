import { InvalidDateError } from "./errors.js";
import type { Weekday } from "./types.js";

export interface CivilDate {
  readonly year: number;
  readonly month: number;
  readonly day: number;
}

const DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;

/**
 * Date-only values are civil dates. UTC accessors keep the calendar day
 * stable in every local timezone, including offsets that would move UTC
 * midnight onto the previous or next local date.
 */
export function parseCivilDate(value: unknown): CivilDate {
  if (typeof value !== "string" || !DATE_PATTERN.test(value)) {
    throw new InvalidDateError(
      `Expected a date-only string in YYYY-MM-DD form, received ${describeReceived(value)}.`,
    );
  }

  const match = DATE_PATTERN.exec(value);
  const yearText = match?.[1];
  const monthText = match?.[2];
  const dayText = match?.[3];
  if (
    yearText === undefined ||
    monthText === undefined ||
    dayText === undefined
  ) {
    throw new InvalidDateError(
      `Expected a date-only string in YYYY-MM-DD form, received ${JSON.stringify(value)}.`,
    );
  }

  const year = Number(yearText);
  const month = Number(monthText);
  const day = Number(dayText);
  if (!isRealCivilDate(year, month, day)) {
    throw new InvalidDateError(`${value} is not a real calendar date.`);
  }

  return { year, month, day };
}

export function civilDateToString(date: CivilDate): string {
  const month = String(date.month).padStart(2, "0");
  const day = String(date.day).padStart(2, "0");
  return `${String(date.year).padStart(4, "0")}-${month}-${day}`;
}

export function civilWeekday(date: CivilDate): Weekday {
  return new Date(Date.UTC(date.year, date.month - 1, date.day)).getUTCDay() as Weekday;
}

export function compareCivilDates(left: CivilDate, right: CivilDate): number {
  if (left.year !== right.year) {
    return left.year - right.year;
  }
  if (left.month !== right.month) {
    return left.month - right.month;
  }
  return left.day - right.day;
}

export function addCivilDays(date: CivilDate, days: number): CivilDate {
  const shifted = new Date(Date.UTC(date.year, date.month - 1, date.day + days));
  return {
    year: shifted.getUTCFullYear(),
    month: shifted.getUTCMonth() + 1,
    day: shifted.getUTCDate(),
  };
}

export function yearsInRange(start: CivilDate, end: CivilDate): number[] {
  const years: number[] = [];
  for (let year = start.year; year <= end.year; year += 1) {
    years.push(year);
  }
  return years;
}

function isRealCivilDate(year: number, month: number, day: number): boolean {
  if (month < 1 || month > 12 || day < 1 || day > 31) {
    return false;
  }
  const utc = new Date(Date.UTC(year, month - 1, day));
  return (
    utc.getUTCFullYear() === year &&
    utc.getUTCMonth() === month - 1 &&
    utc.getUTCDate() === day
  );
}

function describeReceived(value: unknown): string {
  if (typeof value === "string") {
    return JSON.stringify(value);
  }
  if (value === null) {
    return "null";
  }
  if (value instanceof Date) {
    return "a Date object";
  }
  return typeof value;
}
