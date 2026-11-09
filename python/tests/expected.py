"""Annex rows the official dataset must match, including the printed weekday."""

from __future__ import annotations

from dataclasses import dataclass

from indonesia_holidays import HolidayType


@dataclass(frozen=True, slots=True)
class ExpectedHoliday:
    date: str
    name: str
    type: HolidayType
    weekday: str


WEEKDAY_NAMES = ("Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu")


def _row(date: str, name: str, holiday_type: HolidayType, weekday: str) -> ExpectedHoliday:
    return ExpectedHoliday(date=date, name=name, type=holiday_type, weekday=weekday)


EXPECTED_2026: tuple[ExpectedHoliday, ...] = (
    _row("2026-01-01", "Tahun Baru 2026 Masehi", "national_holiday", "Kamis"),
    _row("2026-01-16", "Isra Mikraj Nabi Muhammad S.A.W.", "national_holiday", "Jumat"),
    _row("2026-02-16", "Tahun Baru Imlek 2577 Kongzili", "collective_leave", "Senin"),
    _row("2026-02-17", "Tahun Baru Imlek 2577 Kongzili", "national_holiday", "Selasa"),
    _row("2026-03-18", "Hari Suci Nyepi (Tahun Baru Saka 1948)", "collective_leave", "Rabu"),
    _row("2026-03-19", "Hari Suci Nyepi (Tahun Baru Saka 1948)", "national_holiday", "Kamis"),
    _row("2026-03-20", "Idul Fitri 1447 Hijriah", "collective_leave", "Jumat"),
    _row("2026-03-21", "Idul Fitri 1447 Hijriah", "national_holiday", "Sabtu"),
    _row("2026-03-22", "Idul Fitri 1447 Hijriah", "national_holiday", "Minggu"),
    _row("2026-03-23", "Idul Fitri 1447 Hijriah", "collective_leave", "Senin"),
    _row("2026-03-24", "Idul Fitri 1447 Hijriah", "collective_leave", "Selasa"),
    _row("2026-04-03", "Wafat Yesus Kristus", "national_holiday", "Jumat"),
    _row("2026-04-05", "Kebangkitan Yesus Kristus (Paskah)", "national_holiday", "Minggu"),
    _row("2026-05-01", "Hari Buruh Internasional", "national_holiday", "Jumat"),
    _row("2026-05-14", "Kenaikan Yesus Kristus", "national_holiday", "Kamis"),
    _row("2026-05-15", "Kenaikan Yesus Kristus", "collective_leave", "Jumat"),
    _row("2026-05-27", "Idul Adha 1447 Hijriah", "national_holiday", "Rabu"),
    _row("2026-05-28", "Idul Adha 1447 Hijriah", "collective_leave", "Kamis"),
    _row("2026-05-31", "Hari Raya Waisak 2570 BE", "national_holiday", "Minggu"),
    _row("2026-06-01", "Hari Lahir Pancasila", "national_holiday", "Senin"),
    _row("2026-06-16", "1 Muharam Tahun Baru Islam 1448 Hijriah", "national_holiday", "Selasa"),
    _row("2026-08-17", "Proklamasi Kemerdekaan", "national_holiday", "Senin"),
    _row("2026-08-25", "Maulid Nabi Muhammad S.A.W.", "national_holiday", "Selasa"),
    _row("2026-12-24", "Kelahiran Yesus Kristus", "collective_leave", "Kamis"),
    _row("2026-12-25", "Kelahiran Yesus Kristus", "national_holiday", "Jumat"),
)

EXPECTED_2027: tuple[ExpectedHoliday, ...] = (
    _row("2027-01-01", "Tahun Baru 2027 Masehi", "national_holiday", "Jumat"),
    _row(
        "2027-01-05",
        "Isra Mikraj Nabi Muhammad S.A.W. 1448 Hijriah",
        "national_holiday",
        "Selasa",
    ),
    _row("2027-02-05", "Tahun Baru Imlek 2578 Kongzili", "collective_leave", "Jumat"),
    _row("2027-02-06", "Tahun Baru Imlek 2578 Kongzili", "national_holiday", "Sabtu"),
    _row("2027-03-08", "Hari Suci Nyepi (Tahun Baru Saka 1949)", "national_holiday", "Senin"),
    _row("2027-03-09", "Idul Fitri 1448 Hijriah", "collective_leave", "Selasa"),
    _row("2027-03-10", "Idul Fitri 1448 Hijriah", "national_holiday", "Rabu"),
    _row("2027-03-11", "Idul Fitri 1448 Hijriah", "national_holiday", "Kamis"),
    _row("2027-03-12", "Idul Fitri 1448 Hijriah", "collective_leave", "Jumat"),
    _row("2027-03-15", "Idul Fitri 1448 Hijriah", "collective_leave", "Senin"),
    _row("2027-03-25", "Wafat Yesus Kristus", "collective_leave", "Kamis"),
    _row("2027-03-26", "Wafat Yesus Kristus", "national_holiday", "Jumat"),
    _row("2027-03-28", "Kebangkitan Yesus Kristus (Paskah)", "national_holiday", "Minggu"),
    _row("2027-05-01", "Hari Buruh Internasional", "national_holiday", "Sabtu"),
    _row("2027-05-06", "Kenaikan Yesus Kristus", "national_holiday", "Kamis"),
    _row("2027-05-17", "Idul Adha 1448 Hijriah", "national_holiday", "Senin"),
    _row("2027-05-18", "Idul Adha 1448 Hijriah", "collective_leave", "Selasa"),
    _row("2027-05-19", "Hari Raya Waisak 2571 BE", "collective_leave", "Rabu"),
    _row("2027-05-20", "Hari Raya Waisak 2571 BE", "national_holiday", "Kamis"),
    _row("2027-06-01", "Hari Lahir Pancasila", "national_holiday", "Selasa"),
    _row("2027-06-06", "1 Muharam Tahun Baru Islam 1449 Hijriah", "national_holiday", "Minggu"),
    _row("2027-08-15", "Maulid Nabi Muhammad S.A.W.", "national_holiday", "Minggu"),
    _row("2027-08-17", "Proklamasi Kemerdekaan", "national_holiday", "Selasa"),
    _row("2027-12-24", "Kelahiran Yesus Kristus", "collective_leave", "Jumat"),
    _row("2027-12-25", "Kelahiran Yesus Kristus", "national_holiday", "Sabtu"),
    _row(
        "2027-12-26",
        "Isra Mikraj Nabi Muhammad S.A.W. 1449 Hijriah",
        "national_holiday",
        "Minggu",
    ),
)
