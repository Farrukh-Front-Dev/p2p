"""Sozlamalar klaviaturasi (til tanlash)."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..utils.i18n import t


def get_language_kb(language: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="setlang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en"),
            ],
            [InlineKeyboardButton(text=t("menu_back", language), callback_data="main_menu")],
        ]
    )
