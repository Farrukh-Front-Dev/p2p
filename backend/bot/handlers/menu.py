"""Bosh menyu va kalendar handlerlari."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..keyboards.main_menu import get_calendar_menu_kb, get_main_menu_kb
from ..utils.i18n import t

router = Router()


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.clear()
    await callback.message.edit_text(t("welcome", lang), reply_markup=get_main_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "calendar")
async def show_calendar(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.clear()
    await callback.message.edit_text(
        t("menu_calendar", lang), reply_markup=get_calendar_menu_kb(lang)
    )
    await callback.answer()
