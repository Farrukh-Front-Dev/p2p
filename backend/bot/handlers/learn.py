"""Slot band qilish (mentee) handleri.

Oqim: yo'nalish → mavjud slotlar → boshlanish vaqti → tugash vaqti
(mavjudlik oynasi ichida, maksimal 4 soat) → tasdiq → band qilish (-1 tanga).
"""

from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from ..constants import direction_label
from ..database.models.enums import SlotStatus
from ..database.session import get_db
from ..keyboards.confirm_kb import get_confirm_kb
from ..keyboards.directions_kb import get_directions_single_kb
from ..keyboards.main_menu import get_main_menu_kb
from ..keyboards.slot_list_kb import get_slots_kb
from ..keyboards.time_picker_kb import get_booking_end_kb, get_booking_start_kb
from ..repositories.user_repo import UserRepository
from ..services.coin_service import CoinService
from ..services.notification_service import NotificationService
from ..services.slot_service import SlotService, SlotValidationError
from ..states.learn_states import LearnStates
from ..utils.i18n import t
from ..utils.time_utils import fmt_datetime, fmt_range

router = Router()


@router.callback_query(F.data == "learn_slot")
async def start_learn(callback: CallbackQuery, state: FSMContext, user=None, lang: str = "uz"):
    if user is None or user.coins < 1:
        await callback.answer(t("no_coins", lang), show_alert=True)
        return

    await state.set_state(LearnStates.selecting_direction)
    await callback.message.edit_text(
        t("learn_select_direction", lang),
        reply_markup=get_directions_single_kb(prefix="sdir_"),
    )
    await callback.answer()


@router.callback_query(LearnStates.selecting_direction, F.data.startswith("sdir_"))
async def learn_select_direction(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    direction = callback.data.replace("sdir_", "", 1)
    await state.update_data(direction=direction)

    async with get_db() as db:
        service = SlotService(db)
        slots = await service.get_available_slots(
            direction=direction, exclude_user_id=callback.from_user.id
        )

    if not slots:
        await state.clear()
        await callback.message.edit_text(
            t("learn_no_slots", lang, direction=direction_label(direction)),
            reply_markup=get_main_menu_kb(lang),
        )
        await callback.answer()
        return

    await state.set_state(LearnStates.selecting_slot)
    await callback.message.edit_text(
        t("learn_slot_list", lang, direction=direction_label(direction)),
        reply_markup=get_slots_kb(slots),
    )
    await callback.answer()


@router.callback_query(LearnStates.selecting_slot, F.data.startswith("slot_select_"))
async def learn_select_slot(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    slot_id = callback.data.replace("slot_select_", "", 1)

    async with get_db() as db:
        service = SlotService(db)
        slot = await service.get_slot_by_id(slot_id)

    if slot is None or slot.status != SlotStatus.OPEN.value:
        await callback.answer(t("learn_slot_taken", lang), show_alert=True)
        return

    await state.update_data(
        slot_id=slot_id,
        direction=slot.direction,
        window_start=slot.start_time.isoformat(),
        window_end=slot.end_time.isoformat(),
    )
    await state.set_state(LearnStates.selecting_start)
    await callback.message.edit_text(
        t(
            "learn_select_start",
            lang,
            direction=direction_label(slot.direction),
            window=fmt_range(slot.start_time, slot.end_time),
        ),
        reply_markup=get_booking_start_kb(slot.start_time, slot.end_time),
    )
    await callback.answer()


@router.callback_query(LearnStates.selecting_start, F.data.startswith("bstart_"))
async def learn_select_start(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    iso = callback.data.replace("bstart_", "", 1)
    start = datetime.fromisoformat(iso)
    data = await state.get_data()
    window_end = datetime.fromisoformat(data["window_end"])

    await state.update_data(booking_start=iso)
    await state.set_state(LearnStates.selecting_end)
    await callback.message.edit_text(
        t("learn_select_end", lang, start=fmt_datetime(start)),
        reply_markup=get_booking_end_kb(start, window_end),
    )
    await callback.answer()


@router.callback_query(LearnStates.selecting_end, F.data == "back_to_bstart")
async def learn_back_to_start(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    data = await state.get_data()
    window_start = datetime.fromisoformat(data["window_start"])
    window_end = datetime.fromisoformat(data["window_end"])
    await state.set_state(LearnStates.selecting_start)
    await callback.message.edit_text(
        t(
            "learn_select_start",
            lang,
            direction=direction_label(data["direction"]),
            window=fmt_range(window_start, window_end),
        ),
        reply_markup=get_booking_start_kb(window_start, window_end),
    )
    await callback.answer()


@router.callback_query(LearnStates.selecting_end, F.data.startswith("bend_"))
async def learn_select_end(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    iso = callback.data.replace("bend_", "", 1)
    end = datetime.fromisoformat(iso)
    data = await state.get_data()
    start = datetime.fromisoformat(data["booking_start"])

    await state.update_data(booking_end=iso)
    await state.set_state(LearnStates.confirming)
    await callback.message.edit_text(
        t(
            "learn_confirm",
            lang,
            direction=direction_label(data["direction"]),
            time=fmt_range(start, end),
        ),
        reply_markup=get_confirm_kb("book_slot", lang),
    )
    await callback.answer()


@router.callback_query(LearnStates.confirming, F.data == "confirm_book_slot")
async def learn_confirm(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    data = await state.get_data()
    slot_id = data.get("slot_id")
    booking_start = datetime.fromisoformat(data["booking_start"])
    booking_end = datetime.fromisoformat(data["booking_end"])
    mentee_id = callback.from_user.id

    async with get_db() as db:
        slot_service = SlotService(db)
        coin_service = CoinService(db)

        try:
            booked = await slot_service.book_slot(slot_id, mentee_id, booking_start, booking_end)
        except SlotValidationError:
            booked = False
        if not booked:
            await state.clear()
            await callback.answer(t("learn_slot_taken", lang), show_alert=True)
            await callback.message.edit_text(
                t("learn_book_error", lang), reply_markup=get_main_menu_kb(lang)
            )
            return

        deducted = await coin_service.deduct(mentee_id, 1, reason="spend_learn", slot_id=slot_id)
        if not deducted:
            # Coin yetmadi — band qilishni bekor qilamiz (slotni qaytaramiz)
            await slot_service.repo.release_slot(slot_id)
            await state.clear()
            await callback.answer(t("no_coins", lang), show_alert=True)
            return

        slot = await slot_service.get_slot_by_id(slot_id)
        await db.refresh(slot)
        mentor_repo = UserRepository(db)
        mentor = await mentor_repo.get_by_id(slot.mentor_id)
        slot_direction = slot.direction

    # Mentorga (anonim) xabar
    notifier = NotificationService(callback.bot)
    if mentor is not None:
        await notifier.send(
            mentor.id,
            t(
                "mentor_slot_booked",
                mentor.language,
                direction=direction_label(slot_direction),
                time=fmt_range(booking_start, booking_end),
            ),
        )

    await state.clear()
    await callback.message.edit_text(t("learn_booked", lang), reply_markup=get_main_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "cancel_book_slot")
async def learn_cancel(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.clear()
    await callback.message.edit_text(t("welcome", lang), reply_markup=get_main_menu_kb(lang))
    await callback.answer()
