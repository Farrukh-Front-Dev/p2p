"""Sozlamalar (til o'zgartirish) handleri."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from ..database.session import get_db
from ..keyboards.main_menu import get_main_menu_kb
from ..keyboards.settings_kb import get_language_kb
from ..repositories.user_repo import UserRepository
from ..utils.i18n import SUPPORTED_LANGS, t

router = Router()


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, lang: str = "uz"):
    await callback.message.edit_text(t("settings_title", lang), reply_markup=get_language_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("setlang_"))
async def set_language(callback: CallbackQuery):
    new_lang = callback.data.replace("setlang_", "", 1)
    if new_lang not in SUPPORTED_LANGS:
        await callback.answer()
        return

    async with get_db() as db:
        repo = UserRepository(db)
        await repo.set_language(callback.from_user.id, new_lang)

    await callback.message.edit_text(
        t("settings_language_changed", new_lang),
        reply_markup=get_main_menu_kb(new_lang),
    )
    await callback.answer()
