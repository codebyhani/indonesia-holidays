export class HolidayError extends Error {
  constructor(message: string) {
    super(message);
    this.name = new.target.name;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

/** The value is not a real civil date in `YYYY-MM-DD` form. */
export class InvalidDateError extends HolidayError {}

/** `startDate` is after `endDate`. Both ends of a range are inclusive. */
export class InvalidRangeError extends HolidayError {}

/**
 * The requested year has no dataset. This is thrown instead of treating the
 * year as a year without holidays.
 */
export class UnsupportedYearError extends HolidayError {
  readonly year: number;
  readonly supportedYears: readonly number[];

  constructor(year: number, supportedYears: readonly number[]) {
    const available =
      supportedYears.length > 0 ? supportedYears.join(", ") : "(none)";
    super(
      `No official holiday dataset is available for ${year}. Supported years: ${available}.`,
    );
    this.year = year;
    this.supportedYears = supportedYears;
  }
}

/** An option has the wrong type or an unsupported value. */
export class InvalidOptionError extends HolidayError {}

/** A year file or fixture failed structural checks. */
export class HolidayDataError extends HolidayError {}
