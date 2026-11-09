import {
  addCivilDays,
  civilDateToString,
  civilWeekday,
  compareCivilDates,
  parseCivilDate,
  yearsInRange,
} from "./dates.js";
import {
  HolidayDataError,
  InvalidOptionError,
  InvalidRangeError,
  UnsupportedYearError,
} from "./errors.js";
import type {
  GetHolidaysOptions,
  GetNextHolidayOptions,
  GetWorkingDaysOptions,
  Holiday,
  HolidayType,
  IsHolidayOptions,
  Weekday,
} from "./types.js";
import { validateYearFile } from "./validate.js";

const HOLIDAY_TYPES: readonly HolidayType[] = [
  "national_holiday",
  "collective_leave",
];

const DEFAULT_TYPES: readonly HolidayType[] = HOLIDAY_TYPES;

const DEFAULT_WEEKENDS: readonly Weekday[] = [6, 0];

const TYPE_ORDER: Record<HolidayType, number> = {
  national_holiday: 0,
  collective_leave: 1,
};

export interface HolidayCalendar {
  listSupportedYears(): readonly number[];
  getHolidays(year: number, options?: GetHolidaysOptions): readonly Holiday[];
  isHoliday(date: string, options?: IsHolidayOptions): boolean;
  getHoliday(date: string): Holiday | null;
  getNextHoliday(
    fromDate: string,
    options?: GetNextHolidayOptions,
  ): Holiday | null;
  getWorkingDays(
    startDate: string,
    endDate: string,
    options?: GetWorkingDaysOptions,
  ): number;
}

export function createCalendar(datasets: readonly unknown[]): HolidayCalendar {
  if (!Array.isArray(datasets)) {
    throw new HolidayDataError("Holiday datasets must be an array of year files.");
  }

  const byYear = new Map<number, readonly Holiday[]>();
  for (const dataset of datasets) {
    const validated = validateYearFile(dataset);
    if (byYear.has(validated.year)) {
      throw new HolidayDataError(
        `More than one dataset was provided for ${validated.year}.`,
      );
    }
    const holidays = validated.holidays
      .map((holiday) => freezeHoliday(holiday))
      .sort(compareHolidays);
    byYear.set(validated.year, Object.freeze(holidays));
  }

  const supportedYears = Object.freeze(
    [...byYear.keys()].sort((left, right) => left - right),
  );
  const chronological = supportedYears.flatMap((year) => byYear.get(year) ?? []);
  const byDate = new Map<string, readonly Holiday[]>();
  for (const holiday of chronological) {
    const existing = byDate.get(holiday.date);
    byDate.set(
      holiday.date,
      Object.freeze(existing === undefined ? [holiday] : [...existing, holiday]),
    );
  }

  function requireYear(year: number): readonly Holiday[] {
    const rows = byYear.get(year);
    if (rows === undefined) {
      throw new UnsupportedYearError(year, supportedYears);
    }
    return rows;
  }

  return {
    listSupportedYears() {
      return [...supportedYears];
    },

    getHolidays(year, options) {
      assertOptions(options, "getHolidays");
      assertYear(year);
      const types = resolveTypes(options?.types);
      return requireYear(year).filter((holiday) => types.has(holiday.type));
    },

    isHoliday(date, options) {
      assertOptions(options, "isHoliday");
      const civil = parseCivilDate(date);
      const includeCollectiveLeave = readFlag(
        options?.includeCollectiveLeave,
        "includeCollectiveLeave",
      );
      return requireYear(civil.year).some(
        (holiday) =>
          holiday.date === civilDateToString(civil) &&
          matchesInclusion(holiday, includeCollectiveLeave),
      );
    },

    getHoliday(date) {
      const civil = parseCivilDate(date);
      const matches = requireYear(civil.year).filter(
        (holiday) => holiday.date === civilDateToString(civil),
      );
      const national = matches.find(
        (holiday) => holiday.type === "national_holiday",
      );
      return national ?? matches[0] ?? null;
    },

    getNextHoliday(fromDate, options) {
      assertOptions(options, "getNextHoliday");
      const civil = parseCivilDate(fromDate);
      const inclusive = readFlag(options?.inclusive, "inclusive");
      const includeCollectiveLeave = readFlag(
        options?.includeCollectiveLeave,
        "includeCollectiveLeave",
      );
      const start = inclusive ? civil : addCivilDays(civil, 1);
      for (const holiday of chronological) {
        if (compareCivilDates(parseCivilDate(holiday.date), start) < 0) {
          continue;
        }
        if (matchesInclusion(holiday, includeCollectiveLeave)) {
          return holiday;
        }
      }
      return null;
    },

    getWorkingDays(startDate, endDate, options) {
      assertOptions(options, "getWorkingDays");
      const start = parseCivilDate(startDate);
      const end = parseCivilDate(endDate);
      if (compareCivilDates(start, end) > 0) {
        throw new InvalidRangeError(
          `startDate ${startDate} is after endDate ${endDate}. Both dates are inclusive, so startDate must fall on or before endDate.`,
        );
      }

      for (const year of yearsInRange(start, end)) {
        if (!byYear.has(year)) {
          throw new UnsupportedYearError(year, supportedYears);
        }
      }

      const weekends = resolveWeekends(options?.weekends);
      const includeCollectiveLeave = readFlag(
        options?.includeCollectiveLeave,
        "includeCollectiveLeave",
      );
      let count = 0;
      for (
        let cursor = start;
        compareCivilDates(cursor, end) <= 0;
        cursor = addCivilDays(cursor, 1)
      ) {
        if (weekends.has(civilWeekday(cursor))) {
          continue;
        }
        const rows = byDate.get(civilDateToString(cursor)) ?? [];
        const blocked = rows.some((holiday) =>
          matchesInclusion(holiday, includeCollectiveLeave),
        );
        if (!blocked) {
          count += 1;
        }
      }
      return count;
    },
  };
}

function matchesInclusion(
  holiday: Holiday,
  includeCollectiveLeave: boolean,
): boolean {
  if (holiday.type === "national_holiday") {
    return true;
  }
  return includeCollectiveLeave;
}

function compareHolidays(left: Holiday, right: Holiday): number {
  if (left.date !== right.date) {
    return left.date < right.date ? -1 : 1;
  }
  return TYPE_ORDER[left.type] - TYPE_ORDER[right.type];
}

function assertYear(year: unknown): void {
  if (typeof year !== "number" || !Number.isInteger(year) || year < 1 || year > 9999) {
    throw new InvalidOptionError(
      `Year must be an integer from 1 to 9999, received ${String(year)}.`,
    );
  }
}

function assertOptions(options: unknown, label: string): void {
  if (options === undefined) {
    return;
  }
  if (typeof options !== "object" || options === null || Array.isArray(options)) {
    throw new InvalidOptionError(`${label} options must be an object.`);
  }
}

function readFlag(value: unknown, name: string): boolean {
  if (value === undefined) {
    return false;
  }
  if (typeof value !== "boolean") {
    throw new InvalidOptionError(`${name} must be a boolean.`);
  }
  return value;
}

function resolveTypes(types: unknown): Set<HolidayType> {
  if (types === undefined) {
    return new Set(DEFAULT_TYPES);
  }
  if (!Array.isArray(types)) {
    throw new InvalidOptionError(
      'types must be an array of "national_holiday" and "collective_leave".',
    );
  }
  const resolved = new Set<HolidayType>();
  for (const type of types) {
    if (!isHolidayType(type)) {
      throw new InvalidOptionError(
        `Unknown holiday type ${JSON.stringify(type)}. Use "national_holiday" or "collective_leave".`,
      );
    }
    resolved.add(type);
  }
  return resolved;
}

function resolveWeekends(weekends: unknown): Set<Weekday> {
  const values = weekends === undefined ? DEFAULT_WEEKENDS : weekends;
  if (!Array.isArray(values)) {
    throw new InvalidOptionError(
      "weekends must be an array of weekday numbers from 0 (Sunday) through 6 (Saturday).",
    );
  }
  const resolved = new Set<Weekday>();
  for (const value of values) {
    if (!isWeekday(value)) {
      throw new InvalidOptionError(
        `Invalid weekend day ${String(value)}. Use 0 (Sunday) through 6 (Saturday).`,
      );
    }
    resolved.add(value);
  }
  return resolved;
}

function isHolidayType(value: unknown): value is HolidayType {
  return value === "national_holiday" || value === "collective_leave";
}

function isWeekday(value: unknown): value is Weekday {
  return typeof value === "number" && Number.isInteger(value) && value >= 0 && value <= 6;
}

function freezeHoliday(holiday: Holiday): Holiday {
  const source = holiday.source;
  return Object.freeze({
    date: holiday.date,
    name: holiday.name,
    type: holiday.type,
    source: Object.freeze({
      ...source,
      numbers: Object.freeze(source.numbers.map((number) => Object.freeze({ ...number }))),
      signatories: Object.freeze([...source.signatories]),
      urls: Object.freeze(source.urls.map((url) => Object.freeze({ ...url }))),
      amendments: Object.freeze(
        source.amendments.map((amendment) =>
          Object.freeze({
            ...amendment,
            urls: Object.freeze(amendment.urls.map((url) => Object.freeze({ ...url }))),
          }),
        ),
      ),
      notes: Object.freeze([...source.notes]),
    }),
  });
}
