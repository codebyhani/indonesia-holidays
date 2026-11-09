import { describe, expect, it } from "vitest";
import { createCalendar } from "../src/calendar.js";
import {
  HolidayDataError,
  InvalidOptionError,
  InvalidRangeError,
  UnsupportedYearError,
} from "../src/errors.js";
import leapYear from "./fixtures/leap-2024.json" with { type: "json" };
import duplicateDate from "./fixtures/duplicate-date.json" with { type: "json" };
import duplicateSameType from "./fixtures/duplicate-same-type.json" with { type: "json" };

const leap = createCalendar([leapYear]);
const duplicates = createCalendar([duplicateDate]);

describe("leap-year fixture", () => {
  it("keeps 29 February as a civil date without treating it as official data", () => {
    expect(leapYear.source.title.startsWith("TEST FIXTURE")).toBe(true);
    expect(leap.getHoliday("2024-02-29")).toMatchObject({
      name: "Fixture leap day",
      type: "national_holiday",
    });
    expect(leap.isHoliday("2024-02-29")).toBe(true);
    expect(leap.isHoliday("2024-03-01")).toBe(false);
    expect(leap.isHoliday("2024-03-01", { includeCollectiveLeave: true })).toBe(true);
  });

  it("counts working days across the leap day", () => {
    expect(leap.getWorkingDays("2024-02-28", "2024-03-03")).toBe(2);
    expect(
      leap.getWorkingDays("2024-02-28", "2024-03-03", {
        includeCollectiveLeave: true,
      }),
    ).toBe(1);
  });
});

describe("duplicate dates", () => {
  it("returns the national holiday when both types share a date", () => {
    expect(duplicates.getHoliday("2031-01-01")).toMatchObject({
      name: "Fixture national holiday",
      type: "national_holiday",
    });
    expect(duplicates.getHolidays(2031).map((holiday) => holiday.type)).toEqual([
      "national_holiday",
      "collective_leave",
    ]);
    expect(duplicates.getHoliday("2031-01-01")?.source.amendments).toHaveLength(1);
    expect(Object.isFrozen(duplicates.getHoliday("2031-01-01"))).toBe(true);
  });

  it("rejects two records of the same type on one date", () => {
    expect(() => createCalendar([duplicateSameType])).toThrow(HolidayDataError);
    expect(() => createCalendar([duplicateSameType])).toThrow(/2032-04-01/);
  });
});

describe("missing data and boundaries", () => {
  it("does not treat an absent year as a year without holidays", () => {
    expect(() => leap.getHolidays(2025)).toThrow(UnsupportedYearError);
    expect(() => leap.isHoliday("2025-01-01")).toThrow(UnsupportedYearError);
    expect(() => leap.getHoliday("2028-02-29")).toThrow(UnsupportedYearError);
    expect(() => leap.getWorkingDays("2024-02-28", "2025-01-01")).toThrow(
      UnsupportedYearError,
    );
    try {
      leap.getHolidays(2025);
    } catch (error) {
      expect(error).toBeInstanceOf(UnsupportedYearError);
      expect((error as UnsupportedYearError).year).toBe(2025);
      expect((error as UnsupportedYearError).supportedYears).toEqual([2024]);
    }
  });

  it("returns null from getNextHoliday when no later dataset exists", () => {
    expect(leap.getNextHoliday("2023-12-31")?.date).toBe("2024-02-29");
    expect(leap.getNextHoliday("2024-02-29")).toBeNull();
    expect(leap.getNextHoliday("2024-02-29", { inclusive: true })?.date).toBe(
      "2024-02-29",
    );
    expect(
      leap.getNextHoliday("2024-02-28", { includeCollectiveLeave: true })?.date,
    ).toBe("2024-02-29");
    expect(leap.getNextHoliday("2024-03-01")).toBeNull();
    expect(
      leap.getNextHoliday("2024-03-01", {
        inclusive: true,
        includeCollectiveLeave: true,
      })?.date,
    ).toBe("2024-03-01");
  });

  it("treats both ends as inclusive and rejects a reversed range", () => {
    expect(leap.getWorkingDays("2024-02-28", "2024-02-28")).toBe(1);
    expect(leap.getWorkingDays("2024-02-29", "2024-02-29")).toBe(0);
    expect(leap.getWorkingDays("2024-03-02", "2024-03-02")).toBe(0);
    expect(() => leap.getWorkingDays("2024-03-02", "2024-02-28")).toThrow(
      InvalidRangeError,
    );
  });

  it("honors a custom weekend", () => {
    expect(
      leap.getWorkingDays("2024-03-03", "2024-03-03", { weekends: [5, 6] }),
    ).toBe(1);
    expect(
      leap.getWorkingDays("2024-03-01", "2024-03-01", { weekends: [5, 6] }),
    ).toBe(0);
    expect(
      leap.getWorkingDays("2024-03-02", "2024-03-02", { weekends: [5, 6] }),
    ).toBe(0);
    expect(
      leap.getWorkingDays("2024-02-28", "2024-03-03", { weekends: [0, 1, 2, 3, 4, 5, 6] }),
    ).toBe(0);
  });

  it("rejects invalid options and unsorted duplicate years", () => {
    expect(() => leap.getHolidays(2024.5)).toThrow(InvalidOptionError);
    expect(() =>
      leap.getHolidays(2024, { types: ["observance" as "national_holiday"] }),
    ).toThrow(InvalidOptionError);
    expect(() => leap.isHoliday("2024-02-29", { includeCollectiveLeave: "yes" as unknown as boolean })).toThrow(
      InvalidOptionError,
    );
    expect(() => leap.getWorkingDays("2024-02-28", "2024-02-28", { weekends: [7 as 0] })).toThrow(
      InvalidOptionError,
    );
    expect(() => createCalendar([leapYear, leapYear])).toThrow(HolidayDataError);
    expect(leap.listSupportedYears()).toEqual([2024]);
  });
});

describe("fixture files stay out of production data", () => {
  it("keeps the duplicate fixture labeled as a fixture", () => {
    expect(duplicateSameType.source.kind).toBe("test_fixture");
    expect(duplicateSameType.source.title.startsWith("TEST FIXTURE")).toBe(true);
  });
});
