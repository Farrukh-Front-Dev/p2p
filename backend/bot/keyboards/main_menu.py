"""Bosh menyu va kalendar menyu klaviaturalari."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..utils.i18n import t


def get_main_menu_kb(language: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("menu_calendar", language), callback_data="calendar"),
                InlineKeyboardButton(text=t("menu_profile", language), callback_data="profile"),
            ],
            [
                InlineKeyboardButton(text=t("menu_slots", language), callback_data="my_slots"),
                InlineKeyboardButton(
                    text=t("menu_leaderboard", language), callback_data="leaderboard"
                ),
            ],
            [
                InlineKeyboardButton(text=t("menu_settings", language), callback_data="settings"),
            ],
        ]
    )


def get_calendar_menu_kb(language: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("menu_teach", language), callback_data="teach_slot")],
            [InlineKeyboardButton(text=t("menu_learn", language), callback_data="learn_slot")],
            [InlineKeyboardButton(text=t("menu_slots", language), callback_data="my_slots")],
            [InlineKeyboardButton(text=t("menu_back", language), callback_data="main_menu")],
        ]
    )
