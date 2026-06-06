"""Slot ochish (mentor) handleri.

Oqim: yo'nalish → oylik kalendar (kun) → mavjudlik boshlanish vaqti
(hozirgi soatdan 24:00 gacha) → tasdiq.
Aniq boshlanish/tugashni keyin slotni band qiluvchi (mentee) belgilaydi.
"""

from __future__ import annotations

from datetime import date, datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..constants import direction_label
from ..database.session import get_db
from ..keyboards.confirm_kb import get_confirm_kb
from ..keyboards.directions_kb import get_directions_single_kb
from ..keyboards.main_menu import get_main_menu_kb
from ..keyboards.time_picker_kb import (
    get_calendar_kb,
    get_mentor_end_kb,
    get_mentor_start_kb,
)
from ..services.slot_service import SlotService, SlotValidationError
from ..states.teach_states import TeachStates
from ..utils.i18n import t
from ..utils.time_utils import fmt_datetime, fmt_time, now_local

router = Router()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "teach_slot")
async def start_teach(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.set_state(TeachStates.selecting_direction)
    await callback.message.edit_text(
        t("teach_select_direction", lang),
        reply_markup=get_directions_single_kb(prefix="sdir_"),
    )
    await callback.answer()


@router.callback_query(TeachStates.selecting_direction, F.data.startswith("sdir_"))
async def teach_select_direction(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    direction = callback.data.replace("sdir_", "", 1)
    await state.update_data(direction=direction)
    await state.set_state(TeachStates.selecting_date)
    now = now_local()
    await callback.message.edit_text(
        t("teach_select_date", lang, direction=direction_label(direction)),
        reply_markup=get_calendar_kb(now.year, now.month, now=now),
    )
    await callback.answer()


@router.callback_query(TeachStates.selecting_date, F.data.startswith("calnav_"))
async def teach_calendar_nav(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    _, year, month = callback.data.split("_")
    await callback.message.edit_reply_markup(reply_markup=get_calendar_kb(int(year), int(month)))
    await callback.answer()


@router.callback_query(TeachStates.selecting_date, F.data.startswith("calday_"))
async def teach_select_date(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    iso_date = callback.data.replace("calday_", "", 1)
    target_date = date.fromisoformat(iso_date)
    await state.update_data(date=iso_date)
    await state.set_state(TeachStates.selecting_start_time)
    await callback.message.edit_text(
        t("teach_select_start", lang),
        reply_markup=get_mentor_start_kb(target_date),
    )
    await callback.answer()


@router.callback_query(TeachStates.selecting_start_time, F.data == "back_to_cal")
async def teach_back_to_cal(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    data = await state.get_data()
    now = now_local()
    await state.set_state(TeachStates.selecting_date)
    await callback.message.edit_text(
        t("teach_select_date", lang, direction=direction_label(data["direction"])),
        reply_markup=get_calendar_kb(now.year, now.month, now=now),
    )
    await callback.answer()


@router.callback_query(TeachStates.selecting_start_time, F.data.startswith("mstart_"))
async def teach_select_start(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    iso = callback.data.replace("mstart_", "", 1)
    start_time = datetime.fromisoformat(iso)
    await state.update_data(start_time=iso)
    await state.set_state(TeachStates.selecting_end_time)
    await callback.message.edit_text(
        t("teach_select_end", lang, start=fmt_datetime(start_time)),
        reply_markup=get_mentor_end_kb(start_time),
    )
    await callback.answer()


@router.callback_query(TeachStates.selecting_end_time, F.data == "back_to_mstart")
async def teach_back_to_start(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    data = await state.get_data()
    target_date = date.fromisoformat(data["date"])
    await state.set_state(TeachStates.selecting_start_time)
    await callback.message.edit_text(
        t("teach_select_start", lang),
        reply_markup=get_mentor_start_kb(target_date),
    )
    await callback.answer()


@router.callback_query(TeachStates.selecting_end_time, F.data.startswith("mend_"))
async def teach_select_end(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    iso = callback.data.replace("mend_", "", 1)
    end_time = datetime.fromisoformat(iso)
    data = await state.get_data()
    start_time = datetime.fromisoformat(data["start_time"])
    await state.update_data(end_time=iso)
    await state.set_state(TeachStates.confirming)
    await callback.message.edit_text(
        t(
            "slot_confirm",
            lang,
            direction=direction_label(data["direction"]),
            start=fmt_datetime(start_time),
            end=fmt_time(end_time),
        ),
        reply_markup=get_confirm_kb("slot_create", lang),
    )
    await callback.answer()


@router.callback_query(TeachStates.confirming, F.data == "confirm_slot_create")
async def teach_confirm(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    data = await state.get_data()
    start_time = datetime.fromisoformat(data["start_time"])
    end_time = datetime.fromisoformat(data["end_time"])

    async with get_db() as db:
        service = SlotService(db)
        try:
            await service.create_slot(
                mentor_id=callback.from_user.id,
                direction=data["direction"],
                start_time=start_time,
                end_time=end_time,
            )
        except SlotValidationError as exc:
            await callback.message.edit_text(
                t("slot_invalid_time", lang, error=str(exc)),
                reply_markup=get_main_menu_kb(lang),
            )
            await state.clear()
            await callback.answer()
            return

    await state.clear()
    await callback.message.edit_text(
        t(
            "slot_created",
            lang,
            direction=direction_label(data["direction"]),
            start=fmt_datetime(start_time),
            end=fmt_time(end_time),
        ),
        reply_markup=get_main_menu_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_slot_create")
async def teach_cancel(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.clear()
    await callback.message.edit_text(t("welcome", lang), reply_markup=get_main_menu_kb(lang))
    await callback.answer()
