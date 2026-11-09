/**
 * `national_holiday` is a hari libur nasional.
 * `collective_leave` is cuti bersama. It is not a national holiday.
 */
export type HolidayType = "national_holiday" | "collective_leave";

/**
 * Weekday number for a civil date. `0` is Sunday and `6` is Saturday,
 * matching the ECMAScript weekday numbering without using the local timezone.
 */
export type Weekday = 0 | 1 | 2 | 3 | 4 | 5 | 6;

/** A decree published in the dataset, or a labeled test fixture. */
export type SourceKind = "skb_3_menteri" | "test_fixture";

export interface SourceNumber {
  readonly ministry: string;
  readonly number: string;
}

export interface SourceUrl {
  readonly label: string;
  readonly url: string;
}

/**
 * A later decree that changes an earlier holiday decision.
 * Production years keep this empty until an official amendment is verified.
 */
export interface Amendment {
  readonly id: string;
  readonly title: string;
  readonly issuedOn: string;
  readonly urls: readonly SourceUrl[];
  readonly summary: string;
}

export interface OfficialSource {
  readonly id: string;
  readonly title: string;
  readonly kind: SourceKind;
  readonly numbers: readonly SourceNumber[];
  readonly issuedOn: string;
  readonly place: string;
  readonly signatories: readonly string[];
  readonly urls: readonly SourceUrl[];
  readonly amendments: readonly Amendment[];
  readonly notes: readonly string[];
}

export interface Holiday {
  /** Civil date, `YYYY-MM-DD`. */
  readonly date: string;
  /** Name as printed in the decree annex, in Indonesian. */
  readonly name: string;
  readonly type: HolidayType;
  readonly source: OfficialSource;
}

export interface GetHolidaysOptions {
  /**
   * Holiday types to return. Both types are returned when this is omitted.
   * An empty array returns no rows.
   */
  readonly types?: readonly HolidayType[];
}

export interface IsHolidayOptions {
  /**
   * When `true`, cuti bersama also counts as a holiday.
   * The default is `false`: only hari libur nasional counts.
   */
  readonly includeCollectiveLeave?: boolean;
}

export interface GetNextHolidayOptions {
  /**
   * When `true`, cuti bersama can be returned.
   * The default is `false`.
   */
  readonly includeCollectiveLeave?: boolean;
  /**
   * When `true`, a holiday on `fromDate` itself can be returned.
   * The default is `false`: the search starts on the next civil day.
   */
  readonly inclusive?: boolean;
}

export interface GetWorkingDaysOptions {
  /**
   * Weekdays that are never working days.
   * The default is Saturday and Sunday (`6` and `0`).
   */
  readonly weekends?: readonly Weekday[];
  /**
   * When `true`, cuti bersama is not a working day.
   * The default is `false`, because private-sector collective leave is set
   * by each employer and reduces annual leave when it is taken.
   */
  readonly includeCollectiveLeave?: boolean;
}
