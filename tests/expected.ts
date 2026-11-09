import type { HolidayType } from "../src/types.js";

export interface ExpectedHoliday {
  readonly date: string;
  readonly name: string;
  readonly type: HolidayType;
  /** Weekday printed in the SKB annex. */
  readonly weekday: string;
}

export const EXPECTED_2026: readonly ExpectedHoliday[] = [
  { date: "2026-01-01", name: "Tahun Baru 2026 Masehi", type: "national_holiday", weekday: "Kamis" },
  { date: "2026-01-16", name: "Isra Mikraj Nabi Muhammad S.A.W.", type: "national_holiday", weekday: "Jumat" },
  { date: "2026-02-16", name: "Tahun Baru Imlek 2577 Kongzili", type: "collective_leave", weekday: "Senin" },
  { date: "2026-02-17", name: "Tahun Baru Imlek 2577 Kongzili", type: "national_holiday", weekday: "Selasa" },
  { date: "2026-03-18", name: "Hari Suci Nyepi (Tahun Baru Saka 1948)", type: "collective_leave", weekday: "Rabu" },
  { date: "2026-03-19", name: "Hari Suci Nyepi (Tahun Baru Saka 1948)", type: "national_holiday", weekday: "Kamis" },
  { date: "2026-03-20", name: "Idul Fitri 1447 Hijriah", type: "collective_leave", weekday: "Jumat" },
  { date: "2026-03-21", name: "Idul Fitri 1447 Hijriah", type: "national_holiday", weekday: "Sabtu" },
  { date: "2026-03-22", name: "Idul Fitri 1447 Hijriah", type: "national_holiday", weekday: "Minggu" },
  { date: "2026-03-23", name: "Idul Fitri 1447 Hijriah", type: "collective_leave", weekday: "Senin" },
  { date: "2026-03-24", name: "Idul Fitri 1447 Hijriah", type: "collective_leave", weekday: "Selasa" },
  { date: "2026-04-03", name: "Wafat Yesus Kristus", type: "national_holiday", weekday: "Jumat" },
  { date: "2026-04-05", name: "Kebangkitan Yesus Kristus (Paskah)", type: "national_holiday", weekday: "Minggu" },
  { date: "2026-05-01", name: "Hari Buruh Internasional", type: "national_holiday", weekday: "Jumat" },
  { date: "2026-05-14", name: "Kenaikan Yesus Kristus", type: "national_holiday", weekday: "Kamis" },
  { date: "2026-05-15", name: "Kenaikan Yesus Kristus", type: "collective_leave", weekday: "Jumat" },
  { date: "2026-05-27", name: "Idul Adha 1447 Hijriah", type: "national_holiday", weekday: "Rabu" },
  { date: "2026-05-28", name: "Idul Adha 1447 Hijriah", type: "collective_leave", weekday: "Kamis" },
  { date: "2026-05-31", name: "Hari Raya Waisak 2570 BE", type: "national_holiday", weekday: "Minggu" },
  { date: "2026-06-01", name: "Hari Lahir Pancasila", type: "national_holiday", weekday: "Senin" },
  { date: "2026-06-16", name: "1 Muharam Tahun Baru Islam 1448 Hijriah", type: "national_holiday", weekday: "Selasa" },
  { date: "2026-08-17", name: "Proklamasi Kemerdekaan", type: "national_holiday", weekday: "Senin" },
  { date: "2026-08-25", name: "Maulid Nabi Muhammad S.A.W.", type: "national_holiday", weekday: "Selasa" },
  { date: "2026-12-24", name: "Kelahiran Yesus Kristus", type: "collective_leave", weekday: "Kamis" },
  { date: "2026-12-25", name: "Kelahiran Yesus Kristus", type: "national_holiday", weekday: "Jumat" },
];

export const EXPECTED_2027: readonly ExpectedHoliday[] = [
  { date: "2027-01-01", name: "Tahun Baru 2027 Masehi", type: "national_holiday", weekday: "Jumat" },
  { date: "2027-01-05", name: "Isra Mikraj Nabi Muhammad S.A.W. 1448 Hijriah", type: "national_holiday", weekday: "Selasa" },
  { date: "2027-02-05", name: "Tahun Baru Imlek 2578 Kongzili", type: "collective_leave", weekday: "Jumat" },
  { date: "2027-02-06", name: "Tahun Baru Imlek 2578 Kongzili", type: "national_holiday", weekday: "Sabtu" },
  { date: "2027-03-08", name: "Hari Suci Nyepi (Tahun Baru Saka 1949)", type: "national_holiday", weekday: "Senin" },
  { date: "2027-03-09", name: "Idul Fitri 1448 Hijriah", type: "collective_leave", weekday: "Selasa" },
  { date: "2027-03-10", name: "Idul Fitri 1448 Hijriah", type: "national_holiday", weekday: "Rabu" },
  { date: "2027-03-11", name: "Idul Fitri 1448 Hijriah", type: "national_holiday", weekday: "Kamis" },
  { date: "2027-03-12", name: "Idul Fitri 1448 Hijriah", type: "collective_leave", weekday: "Jumat" },
  { date: "2027-03-15", name: "Idul Fitri 1448 Hijriah", type: "collective_leave", weekday: "Senin" },
  { date: "2027-03-25", name: "Wafat Yesus Kristus", type: "collective_leave", weekday: "Kamis" },
  { date: "2027-03-26", name: "Wafat Yesus Kristus", type: "national_holiday", weekday: "Jumat" },
  { date: "2027-03-28", name: "Kebangkitan Yesus Kristus (Paskah)", type: "national_holiday", weekday: "Minggu" },
  { date: "2027-05-01", name: "Hari Buruh Internasional", type: "national_holiday", weekday: "Sabtu" },
  { date: "2027-05-06", name: "Kenaikan Yesus Kristus", type: "national_holiday", weekday: "Kamis" },
  { date: "2027-05-17", name: "Idul Adha 1448 Hijriah", type: "national_holiday", weekday: "Senin" },
  { date: "2027-05-18", name: "Idul Adha 1448 Hijriah", type: "collective_leave", weekday: "Selasa" },
  { date: "2027-05-19", name: "Hari Raya Waisak 2571 BE", type: "collective_leave", weekday: "Rabu" },
  { date: "2027-05-20", name: "Hari Raya Waisak 2571 BE", type: "national_holiday", weekday: "Kamis" },
  { date: "2027-06-01", name: "Hari Lahir Pancasila", type: "national_holiday", weekday: "Selasa" },
  { date: "2027-06-06", name: "1 Muharam Tahun Baru Islam 1449 Hijriah", type: "national_holiday", weekday: "Minggu" },
  { date: "2027-08-15", name: "Maulid Nabi Muhammad S.A.W.", type: "national_holiday", weekday: "Minggu" },
  { date: "2027-08-17", name: "Proklamasi Kemerdekaan", type: "national_holiday", weekday: "Selasa" },
  { date: "2027-12-24", name: "Kelahiran Yesus Kristus", type: "collective_leave", weekday: "Jumat" },
  { date: "2027-12-25", name: "Kelahiran Yesus Kristus", type: "national_holiday", weekday: "Sabtu" },
  { date: "2027-12-26", name: "Isra Mikraj Nabi Muhammad S.A.W. 1449 Hijriah", type: "national_holiday", weekday: "Minggu" },
];

export const WEEKDAY_NAMES = [
  "Minggu",
  "Senin",
  "Selasa",
  "Rabu",
  "Kamis",
  "Jumat",
  "Sabtu",
] as const;
