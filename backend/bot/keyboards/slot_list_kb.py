"""Slotlar ro'yxati klaviaturasi (anonim — mentor ko'rsatilmaydi)."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..utils.time_utils import fmt_range


def get_slots_kb(slots) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for slot in slots:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"⏰ {fmt_range(slot.start_time, slot.end_time)}",
                    callback_data=f"slot_select_{slot.id}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)
