"""Yo'nalishlar klaviaturasi."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..constants import DIRECTIONS
from ..utils.i18n import t


def get_directions_kb(selected: list[str], language: str = "uz") -> InlineKeyboardMarkup:
    """Ko'p tanlovli yo'nalishlar (ro'yxatdan o'tish uchun)."""
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for d in DIRECTIONS:
        mark = "✅ " if d["id"] in selected else ""
        row.append(
            InlineKeyboardButton(
                text=f"{mark}{d['emoji']} {d['name']}",
                callback_data=f"dir_{d['id']}",
            )
        )
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append(
        [InlineKeyboardButton(text=t("btn_confirm", language), callback_data="dir_confirm")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_directions_single_kb(
    prefix: str = "sdir_", back_cb: str | None = "calendar", language: str = "uz"
) -> InlineKeyboardMarkup:
    """Bitta tanlovli yo'nalishlar (slot ochish/band qilish uchun)."""
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for d in DIRECTIONS:
        row.append(
            InlineKeyboardButton(
                text=f"{d['emoji']} {d['name']}",
                callback_data=f"{prefix}{d['id']}",
            )
        )
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    if back_cb:
        rows.append([InlineKeyboardButton(text=t("menu_back", language), callback_data=back_cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)
