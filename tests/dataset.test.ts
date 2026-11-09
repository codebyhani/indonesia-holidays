import { describe, expect, it } from "vitest";
import { civilWeekday, parseCivilDate } from "../src/dates.js";
import { UnsupportedYearError } from "../src/errors.js";
import {
  getHoliday,
  getHolidays,
  getNextHoliday,
  getWorkingDays,
  isHoliday,
  listSupportedYears,
} from "../src/index.js";
import { WEEKDAY_NAMES, EXPECTED_2026, EXPECTED_2027, type ExpectedHoliday } from "./expected.js";

describe("official datasets", () => {
  it("ships 2026 and 2027 only", () => {
    expect(listSupportedYears()).toEqual([2026, 2027]);
  });

  it.each([
    [2026, EXPECTED_2026, 17, 8],
    [2027, EXPECTED_2027, 18, 8],
  ] as const)(
    "matches the %i SKB annex, including printed weekdays",
    (year, expected, nationalCount, collectiveCount) => {
      const holidays = getHolidays(year);
      expect(holidays.map(toExpected)).toEqual(expected);
      expect(new Set(holidays.map((holiday) => holiday.date)).size).toBe(holidays.length);
      expect(holidays.filter((holiday) => holiday.type === "national_holiday")).toHaveLength(
        nationalCount,
      );
      expect(holidays.filter((holiday) => holiday.type === "collective_leave")).toHaveLength(
        collectiveCount,
      );

      for (const holiday of holidays) {
        const weekday = civilWeekday(parseCivilDate(holiday.date));
        const printed = WEEKDAY_NAMES[weekday];
        const row = expected.find((item) => item.date === holiday.date);
        expect(printed).toBe(row?.weekday);
        expect(holiday.source.kind).toBe("skb_3_menteri");
        expect(holiday.source.title.startsWith("TEST FIXTURE")).toBe(false);
        expect(holiday.source.amendments).toEqual([]);
        expect(holiday.source.numbers.length).toBeGreaterThanOrEqual(3);
        expect(holiday.source.urls.every((url) => url.url.startsWith("https://"))).toBe(true);
        expect(holiday.date.startsWith(`${year}-`)).toBe(true);
      }
    },
  );

  it("keeps cuti bersama out of the default holiday and working-day results", () => {
    expect(isHoliday("2026-02-16")).toBe(false);
    expect(isHoliday("2026-02-16", { includeCollectiveLeave: true })).toBe(true);
    expect(isHoliday("2026-02-17")).toBe(true);
    expect(getHoliday("2026-02-16")?.type).toBe("collective_leave");
    expect(getHoliday("2026-01-02")).toBeNull();

    expect(getWorkingDays("2026-01-01", "2026-01-31")).toBe(20);
    expect(getWorkingDays("2026-02-01", "2026-02-28")).toBe(19);
    expect(
      getWorkingDays("2026-02-01", "2026-02-28", { includeCollectiveLeave: true }),
    ).toBe(18);
    expect(getWorkingDays("2026-01-01", "2026-01-01")).toBe(0);
    expect(getWorkingDays("2026-01-02", "2026-01-02")).toBe(1);
    expect(getWorkingDays("2026-01-03", "2026-01-03")).toBe(0);
    expect(getWorkingDays("2026-12-31", "2027-01-01")).toBe(1);
  });

  it("walks forward through supported years and stops when the data ends", () => {
    expect(getNextHoliday("2025-12-31")?.date).toBe("2026-01-01");
    expect(getNextHoliday("2026-01-01")?.date).toBe("2026-01-16");
    expect(getNextHoliday("2026-01-01", { inclusive: true })?.date).toBe("2026-01-01");
    expect(getNextHoliday("2026-02-16")?.date).toBe("2026-02-17");
    expect(
      getNextHoliday("2026-02-15", { includeCollectiveLeave: true })?.date,
    ).toBe("2026-02-16");
    expect(getNextHoliday("2026-12-25")?.date).toBe("2027-01-01");
    expect(getNextHoliday("2026-12-23", { includeCollectiveLeave: true })?.date).toBe(
      "2026-12-24",
    );
    expect(getNextHoliday("2027-12-25")?.date).toBe("2027-12-26");
    expect(getNextHoliday("2027-12-26")).toBeNull();
    expect(getNextHoliday("2028-01-01")).toBeNull();
    expect(getHolidays(2026, { types: ["national_holiday"] })).toHaveLength(17);
    expect(getHolidays(2027, { types: ["collective_leave"] })).toHaveLength(8);
    expect(getHolidays(2026, { types: [] })).toEqual([]);
  });

  it("can treat Friday and Saturday as the weekend", () => {
    expect(
      getWorkingDays("2026-01-02", "2026-01-04", { weekends: [5, 6] }),
    ).toBe(1);
  });

  it("rejects a range that leaves the shipped years", () => {
    expect(() => getHolidays(2025)).toThrow(UnsupportedYearError);
    expect(() => getHoliday("2024-02-29")).toThrow(UnsupportedYearError);
    expect(() => getWorkingDays("2027-12-31", "2028-01-02")).toThrow(
      UnsupportedYearError,
    );
  });
});

function toExpected(holiday: {
  date: string;
  name: string;
  type: ExpectedHoliday["type"];
}): Omit<ExpectedHoliday, "weekday"> & { weekday?: string } {
  return {
    date: holiday.date,
    name: holiday.name,
    type: holiday.type,
    weekday: WEEKDAY_NAMES[civilWeekday(parseCivilDate(holiday.date))],
  };
}
