import { describe, expect, it } from "vitest";
import { addCivilDays, civilWeekday, parseCivilDate } from "../src/dates.js";
import { InvalidDateError } from "../src/errors.js";

/**
 * Independent Gregorian weekday, 0 = Sunday.
 * Sakamoto's method does not use `Date`, so it checks the civil-date math
 * even when the process timezone would move a UTC midnight timestamp.
 */
function sakamotoWeekday(year: number, month: number, day: number): number {
  const offsets = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4];
  const offset = offsets[month - 1];
  if (offset === undefined) {
    throw new Error(`Invalid month ${month}.`);
  }
  let adjustedYear = year;
  if (month < 3) {
    adjustedYear -= 1;
  }
  return (
    (adjustedYear +
      Math.floor(adjustedYear / 4) -
      Math.floor(adjustedYear / 100) +
      Math.floor(adjustedYear / 400) +
      offset +
      day) %
    7
  );
}

describe("civil dates", () => {
  it("accepts leap day in 2024 and 2000 and rejects it in 2026 and 1900", () => {
    expect(parseCivilDate("2024-02-29")).toEqual({ year: 2024, month: 2, day: 29 });
    expect(parseCivilDate("2000-02-29")).toEqual({ year: 2000, month: 2, day: 29 });
    expect(() => parseCivilDate("2026-02-29")).toThrow(InvalidDateError);
    expect(() => parseCivilDate("1900-02-29")).toThrow(InvalidDateError);
  });

  it("rejects dates that are not real calendar days", () => {
    for (const value of [
      "2026-04-31",
      "2026-00-10",
      "2026-01-00",
      "2026-13-01",
      "",
      "2026/01/01",
      "2026-1-01",
      " 2026-01-01",
      "2026-01-01 ",
    ]) {
      expect(() => parseCivilDate(value)).toThrow(InvalidDateError);
    }
    expect(() => parseCivilDate(new Date("2026-01-01T00:00:00.000Z"))).toThrow(
      InvalidDateError,
    );
  });

  it("matches an independent weekday formula, including across a leap day", () => {
    const samples = [
      "2026-01-01",
      "2024-02-28",
      "2024-02-29",
      "2024-03-01",
      "2026-12-31",
      "2027-01-01",
      "1900-03-01",
      "2000-02-29",
    ];
    for (const value of samples) {
      const date = parseCivilDate(value);
      expect(civilWeekday(date)).toBe(sakamotoWeekday(date.year, date.month, date.day));
    }
  });

  it("adds days across month and leap-year boundaries", () => {
    expect(addCivilDays(parseCivilDate("2024-02-28"), 1)).toEqual({
      year: 2024,
      month: 2,
      day: 29,
    });
    expect(addCivilDays(parseCivilDate("2026-02-28"), 1)).toEqual({
      year: 2026,
      month: 3,
      day: 1,
    });
    expect(addCivilDays(parseCivilDate("2026-12-31"), 1)).toEqual({
      year: 2027,
      month: 1,
      day: 1,
    });
  });
});
