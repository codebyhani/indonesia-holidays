import { parseCivilDate } from "./dates.js";
import { HolidayDataError } from "./errors.js";
import type {
  Amendment,
  Holiday,
  HolidayType,
  OfficialSource,
  SourceKind,
  SourceNumber,
  SourceUrl,
} from "./types.js";

export interface ValidatedYear {
  readonly year: number;
  readonly source: OfficialSource;
  readonly holidays: readonly Holiday[];
}

const HOLIDAY_TYPES = new Set<HolidayType>([
  "national_holiday",
  "collective_leave",
]);

const SOURCE_KINDS = new Set<SourceKind>(["skb_3_menteri", "test_fixture"]);

export function validateYearFile(input: unknown): ValidatedYear {
  const record = expectRecord(input, "Year file");
  assertExactKeys(record, ["year", "source", "holidays"], "Year file");

  const year = expectInteger(record.year, "Year file year");
  if (year < 1 || year > 9999) {
    throw new HolidayDataError(`Year file year ${year} is outside 1..9999.`);
  }

  const source = validateSource(record.source);
  const holidaysInput = expectArray(record.holidays, "Year file holidays");
  const seen = new Set<string>();
  const holidays: Holiday[] = [];

  for (const [index, entry] of holidaysInput.entries()) {
    const holiday = validateHoliday(entry, year, source, index);
    const key = `${holiday.date}:${holiday.type}`;
    if (seen.has(key)) {
      throw new HolidayDataError(
        `Duplicate ${holiday.type} on ${holiday.date} in ${source.id}.`,
      );
    }
    seen.add(key);
    holidays.push(holiday);
  }

  return { year, source, holidays };
}

function validateSource(input: unknown): OfficialSource {
  const record = expectRecord(input, "Source");
  assertExactKeys(
    record,
    [
      "id",
      "title",
      "kind",
      "numbers",
      "issuedOn",
      "place",
      "signatories",
      "urls",
      "amendments",
      "notes",
    ],
    "Source",
  );

  const id = expectNonEmptyString(record.id, "Source id");
  const title = expectNonEmptyString(record.title, "Source title");
  const kind = expectSourceKind(record.kind);
  if (kind === "test_fixture" && !title.startsWith("TEST FIXTURE")) {
    throw new HolidayDataError(
      `Test fixture source ${id} must use a title that starts with "TEST FIXTURE".`,
    );
  }
  if (kind === "skb_3_menteri" && title.startsWith("TEST FIXTURE")) {
    throw new HolidayDataError(
      `Official source ${id} is labeled as a test fixture.`,
    );
  }

  const numbers = expectArray(record.numbers, "Source numbers").map((entry, index) =>
    validateNumber(entry, index),
  );
  if (numbers.length === 0) {
    throw new HolidayDataError(`Source ${id} needs at least one decree number.`);
  }

  const issuedOn = expectDateString(record.issuedOn, "Source issuedOn");
  const place = expectNonEmptyString(record.place, "Source place");
  const signatories = expectStringList(record.signatories, "Source signatories");
  if (signatories.length === 0) {
    throw new HolidayDataError(`Source ${id} needs at least one signatory.`);
  }

  const urls = expectArray(record.urls, "Source urls").map((entry, index) =>
    validateUrl(entry, `Source url ${index}`),
  );
  if (urls.length === 0) {
    throw new HolidayDataError(`Source ${id} needs at least one URL.`);
  }

  const amendments = expectArray(record.amendments, "Source amendments").map(
    (entry, index) => validateAmendment(entry, index),
  );
  const notes = expectStringList(record.notes, "Source notes");

  return {
    id,
    title,
    kind,
    numbers,
    issuedOn,
    place,
    signatories,
    urls,
    amendments,
    notes,
  };
}

function validateHoliday(
  input: unknown,
  year: number,
  source: OfficialSource,
  index: number,
): Holiday {
  const label = `Holiday ${index} in ${source.id}`;
  const record = expectRecord(input, label);
  assertExactKeys(record, ["date", "name", "type", "sourceId"], label);

  const date = expectDateString(record.date, `${label} date`);
  const parsed = parseCivilDate(date);
  if (parsed.year !== year) {
    throw new HolidayDataError(
      `${date} is listed in the ${year} dataset (${source.id}).`,
    );
  }

  const name = expectNonEmptyString(record.name, `${label} name`);
  const type = expectHolidayType(record.type, label);
  const sourceId = expectNonEmptyString(record.sourceId, `${label} sourceId`);
  if (sourceId !== source.id) {
    throw new HolidayDataError(
      `${label} sourceId ${sourceId} does not match source ${source.id}.`,
    );
  }

  return { date, name, type, source };
}

function validateNumber(input: unknown, index: number): SourceNumber {
  const label = `Source number ${index}`;
  const record = expectRecord(input, label);
  assertExactKeys(record, ["ministry", "number"], label);
  return {
    ministry: expectNonEmptyString(record.ministry, `${label} ministry`),
    number: expectNonEmptyString(record.number, `${label} number`),
  };
}

function validateUrl(input: unknown, label: string): SourceUrl {
  const record = expectRecord(input, label);
  assertExactKeys(record, ["label", "url"], label);
  const urlLabel = expectNonEmptyString(record.label, `${label} label`);
  const url = expectNonEmptyString(record.url, `${label} url`);
  if (!/^https:\/\/\S+$/.test(url)) {
    throw new HolidayDataError(`${label} must be an absolute https URL: ${url}.`);
  }
  return { label: urlLabel, url };
}

function validateAmendment(input: unknown, index: number): Amendment {
  const label = `Amendment ${index}`;
  const record = expectRecord(input, label);
  assertExactKeys(
    record,
    ["id", "title", "issuedOn", "urls", "summary"],
    label,
  );
  const urls = expectArray(record.urls, `${label} urls`).map((entry, urlIndex) =>
    validateUrl(entry, `${label} url ${urlIndex}`),
  );
  if (urls.length === 0) {
    throw new HolidayDataError(`${label} needs at least one URL.`);
  }
  return {
    id: expectNonEmptyString(record.id, `${label} id`),
    title: expectNonEmptyString(record.title, `${label} title`),
    issuedOn: expectDateString(record.issuedOn, `${label} issuedOn`),
    urls,
    summary: expectNonEmptyString(record.summary, `${label} summary`),
  };
}

function expectHolidayType(value: unknown, label: string): HolidayType {
  if (typeof value === "string" && HOLIDAY_TYPES.has(value as HolidayType)) {
    return value as HolidayType;
  }
  throw new HolidayDataError(
    `${label} type must be "national_holiday" or "collective_leave".`,
  );
}

function expectSourceKind(value: unknown): SourceKind {
  if (typeof value === "string" && SOURCE_KINDS.has(value as SourceKind)) {
    return value as SourceKind;
  }
  throw new HolidayDataError(
    'Source kind must be "skb_3_menteri" or "test_fixture".',
  );
}

function expectDateString(value: unknown, label: string): string {
  if (typeof value !== "string") {
    throw new HolidayDataError(`${label} must be a YYYY-MM-DD string.`);
  }
  parseCivilDate(value);
  return value;
}

function expectRecord(
  value: unknown,
  label: string,
): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new HolidayDataError(`${label} must be an object.`);
  }
  return value as Record<string, unknown>;
}

function expectArray(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) {
    throw new HolidayDataError(`${label} must be an array.`);
  }
  return value;
}

function expectNonEmptyString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.trim() === "" || value !== value.trim()) {
    throw new HolidayDataError(`${label} must be a non-empty string without surrounding whitespace.`);
  }
  return value;
}

function expectStringList(value: unknown, label: string): string[] {
  return expectArray(value, label).map((entry, index) =>
    expectNonEmptyString(entry, `${label} ${index}`),
  );
}

function expectInteger(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isInteger(value)) {
    throw new HolidayDataError(`${label} must be an integer.`);
  }
  return value;
}

function assertExactKeys(
  record: Record<string, unknown>,
  keys: readonly string[],
  label: string,
): void {
  const actual = Object.keys(record);
  const expected = new Set(keys);
  for (const key of actual) {
    if (!expected.has(key)) {
      throw new HolidayDataError(`${label} has unknown property "${key}".`);
    }
  }
  for (const key of keys) {
    if (!Object.prototype.hasOwnProperty.call(record, key)) {
      throw new HolidayDataError(`${label} is missing "${key}".`);
    }
  }
}
