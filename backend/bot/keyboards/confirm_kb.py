"""Tasdiqlash/bekor qilish klaviaturasi."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..utils.i18n import t


def get_confirm_kb(action: str, language: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_confirm", language),
                    callback_data=f"confirm_{action}",
                ),
                InlineKeyboardButton(
                    text=t("btn_cancel", language),
                    callback_data=f"cancel_{action}",
                ),
            ]
        ]
    )
