"""Oylik kalendar va vaqt tanlash klaviaturalari (School 21 uslubida).

- Oylik panjara: ◀ ▶ bilan oy almashtirish, o'tgan kunlar bloklangan.
- Mentor: kun tanlab, mavjudlik boshlanish vaqtini belgilaydi (hozirgi
  soatdan 24:00 gacha). Mavjudlik oynasi: [boshlanish ... 24:00].
- Mentee: slotni band qilishda boshlanish va tugash vaqtini belgilaydi
  (oynaning ichida, maksimal 4 soat).

Callback formatlari:
  calnav_<YYYY>_<MM>            — oyni almashtirish
  calday_<YYYY-MM-DD>          — kun tanlash
  mstart_<ISO>                 — mentor mavjudlik boshlanishi
  bstart_<ISO>                 — mentee boshlanish vaqti
  bend_<ISO>                   — mentee tugash vaqti
  noop                         — bo'sh/bloklangan tugma
"""

from __future__ import annotations

import calendar as _calmod
from datetime import date, datetime, time, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..utils.time_utils import now_local

_STEP_MINUTES = 30
_TIMES_PER_ROW = 4
_MONTHS_AHEAD = 6
_MAX_DURATION_HOURS = 4

_MONTHS_UZ = [
    "Yanvar",
    "Fevral",
    "Mart",
    "Aprel",
    "May",
    "Iyun",
    "Iyul",
    "Avgust",
    "Sentabr",
    "Oktabr",
    "Noyabr",
    "Dekabr",
]
_WEEKDAYS_UZ = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"]


# ---------------------------------------------------------------- Kalendar


def _month_index(year: int, month: int) -> int:
    return year * 12 + (month - 1)


def get_calendar_kb(year: int, month: int, now: datetime | None = None) -> InlineKeyboardMarkup:
    """Berilgan oy uchun oylik panjara klaviaturasi."""
    now = now or now_local()
    today = now.date()
    cur_idx = _month_index(today.year, today.month)
    this_idx = _month_index(year, month)
    max_idx = cur_idx + _MONTHS_AHEAD

    rows: list[list[InlineKeyboardButton]] = []

    # Navigatsiya qatori: ◀  Oy Yil  ▶
    prev_y, prev_m = (year - 1, 12) if month == 1 else (year, month - 1)
    next_y, next_m = (year + 1, 1) if month == 12 else (year, month + 1)

    left = (
        InlineKeyboardButton(text="◀", callback_data=f"calnav_{prev_y}_{prev_m}")
        if this_idx > cur_idx
        else InlineKeyboardButton(text=" ", callback_data="noop")
    )
    right = (
        InlineKeyboardButton(text="▶", callback_data=f"calnav_{next_y}_{next_m}")
        if this_idx < max_idx
        else InlineKeyboardButton(text=" ", callback_data="noop")
    )
    title = InlineKeyboardButton(text=f"{_MONTHS_UZ[month - 1]} {year}", callback_data="noop")
    rows.append([left, title, right])

    # Hafta kunlari sarlavhasi
    rows.append([InlineKeyboardButton(text=w, callback_data="noop") for w in _WEEKDAYS_UZ])

    # Kunlar panjarasi (Dushanba — birinchi kun)
    for week in _calmod.Calendar(firstweekday=0).monthdayscalendar(year, month):
        row: list[InlineKeyboardButton] = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="noop"))
                continue
            d = date(year, month, day)
            if d < today:
                # O'tgan kun — bloklangan
                row.append(InlineKeyboardButton(text="·", callback_data="noop"))
            else:
                mark = "🔹" if d == today else ""
                row.append(
                    InlineKeyboardButton(
                        text=f"{mark}{day}",
                        callback_data=f"calday_{d.isoformat()}",
                    )
                )
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------------------------------------------------------------- Vaqt


def _round_up_to_step(dt: datetime, step: int = _STEP_MINUTES) -> datetime:
    dt = dt.replace(second=0, microsecond=0)
    rem = dt.minute % step
    if rem:
        dt += timedelta(minutes=step - rem)
    return dt


def _day_end(target_date: date) -> datetime:
    """Tanlangan kun uchun 24:00 (keyingi kun 00:00)."""
    return datetime.combine(target_date, time(0, 0)) + timedelta(days=1)


def _build_time_kb(slots: list[datetime], prefix: str, back_cb: str | None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for dt in slots:
        row.append(
            InlineKeyboardButton(
                text=dt.strftime("%H:%M"),
                callback_data=f"{prefix}{dt.isoformat()}",
            )
        )
        if len(row) == _TIMES_PER_ROW:
            rows.append(row)
            row = []
    if row:
        while len(row) < _TIMES_PER_ROW:
            row.append(InlineKeyboardButton(text=" ", callback_data="noop"))
        rows.append(row)
    if back_cb:
        rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=back_cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def mentor_start_slots(target_date: date, now: datetime) -> list[datetime]:
    """Mentor mavjudlik boshlanishi: hozirgi soatdan (bugun) 24:00 gacha."""
    end = _day_end(target_date)
    if target_date == now.date():
        # Hozirgi vaqtni keyingi 30 daqiqalik chegaraga yaxlitlaymiz
        start = _round_up_to_step(now)
        if start <= now:
            start += timedelta(minutes=_STEP_MINUTES)
    else:
        start = datetime.combine(target_date, time(0, 0))
    slots: list[datetime] = []
    cur = start
    # Oxirgi boshlanish 24:00 dan oldin bo'lishi kerak (kamida 30 daqiqa qoladi)
    while cur < end:
        slots.append(cur)
        cur += timedelta(minutes=_STEP_MINUTES)
    return slots


def get_mentor_start_kb(target_date: date, now: datetime | None = None) -> InlineKeyboardMarkup:
    now = now or now_local()
    return _build_time_kb(
        mentor_start_slots(target_date, now), prefix="mstart_", back_cb="back_to_cal"
    )


def get_mentor_end_kb(
    chosen_start: datetime, target_date: date | None = None
) -> InlineKeyboardMarkup:
    """Mentor tugash vaqti: (start+30min ... 24:00]. Mentor uchun cheklov yo'q."""
    day_end = _day_end(chosen_start.date())
    slots: list[datetime] = []
    cur = chosen_start + timedelta(minutes=_STEP_MINUTES)
    while cur <= day_end:
        slots.append(cur)
        cur += timedelta(minutes=_STEP_MINUTES)
    return _build_time_kb(slots, prefix="mend_", back_cb="back_to_mstart")


def get_booking_start_kb(window_start: datetime, window_end: datetime) -> InlineKeyboardMarkup:
    """Mentee boshlanish vaqti: [window_start ... window_end - 30min]."""
    slots: list[datetime] = []
    cur = window_start
    while cur < window_end:
        slots.append(cur)
        cur += timedelta(minutes=_STEP_MINUTES)
    return _build_time_kb(slots, prefix="bstart_", back_cb=None)


def get_booking_end_kb(chosen_start: datetime, window_end: datetime) -> InlineKeyboardMarkup:
    """Mentee tugash vaqti: (start ... min(start+4soat, window_end)]."""
    max_end = min(chosen_start + timedelta(hours=_MAX_DURATION_HOURS), window_end)
    slots: list[datetime] = []
    cur = chosen_start + timedelta(minutes=_STEP_MINUTES)
    while cur <= max_end:
        slots.append(cur)
        cur += timedelta(minutes=_STEP_MINUTES)
    return _build_time_kb(slots, prefix="bend_", back_cb="back_to_bstart")
