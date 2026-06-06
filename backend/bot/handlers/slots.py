"""Mening slotlarim, reyting jadvali, slot bekor qilish va tahrirlash."""

from __future__ import annotations

from datetime import date, datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from ..constants import direction_label
from ..database.session import get_db
from ..keyboards.directions_kb import get_directions_single_kb
from ..keyboards.main_menu import get_main_menu_kb
from ..keyboards.time_picker_kb import (
    get_calendar_kb,
    get_mentor_end_kb,
    get_mentor_start_kb,
)
from ..repositories.slot_repo import SlotRepository
from ..repositories.user_repo import UserRepository
from ..services.notification_service import NotificationService
from ..services.slot_service import SlotService, SlotValidationError
from ..states.edit_states import EditStates
from ..utils.i18n import t
from ..utils.time_utils import fmt_datetime, fmt_range, now_local

router = Router()

_STATUS_KEY = {
    "open": "slot_status_open",
    "booked": "slot_status_booked",
    "reminded": "slot_status_reminded",
    "active": "slot_status_active",
    "finished": "slot_status_finished",
    "cancelled": "slot_status_cancelled",
}

# Bekor qilinishi mumkin bo'lgan statuslar
_CANCELLABLE = {"open", "booked", "reminded"}


def _back_button(lang: str, target: str = "main_menu") -> InlineKeyboardButton:
    return InlineKeyboardButton(text=t("menu_back", lang), callback_data=target)


def _my_slots_kb(slots, user_id: int, lang: str) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for slot in slots:
        if slot.mentor_id != user_id:
            continue
        label = f"{direction_label(slot.direction)} {fmt_range(slot.start_time, slot.end_time)}"
        # Ochiq slot — tahrirlash + bekor qilish
        if slot.status == "open":
            rows.append(
                [
                    InlineKeyboardButton(
                        text=f"{t('slot_edit_btn', lang)} · {label}",
                        callback_data=f"slotedit_{slot.id}",
                    )
                ]
            )
            rows.append(
                [
                    InlineKeyboardButton(
                        text=t("slot_cancel_btn", lang),
                        callback_data=f"slot_cancel_{slot.id}",
                    )
                ]
            )
        elif slot.status in _CANCELLABLE:
            rows.append(
                [
                    InlineKeyboardButton(
                        text=f"{t('slot_cancel_btn', lang)} · {label}",
                        callback_data=f"slot_cancel_{slot.id}",
                    )
                ]
            )
    rows.append([_back_button(lang)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _render_my_slots(callback: CallbackQuery, lang: str) -> None:
    user_id = callback.from_user.id
    async with get_db() as db:
        slots = await SlotRepository(db).get_user_slots(user_id)

    if not slots:
        await callback.message.edit_text(
            t("my_slots_empty", lang), reply_markup=get_main_menu_kb(lang)
        )
        return

    lines = [t("my_slots_title", lang), ""]
    for slot in slots:
        role_key = "slot_role_mentor" if slot.mentor_id == user_id else "slot_role_mentee"
        status_key = _STATUS_KEY.get(slot.status, "slot_status_open")
        lines.append(
            f"{t(role_key, lang)} · {direction_label(slot.direction)}\n"
            f"   ⏰ {fmt_range(slot.start_time, slot.end_time)} · {t(status_key, lang)}"
        )
    await callback.message.edit_text(
        "\n".join(lines), reply_markup=_my_slots_kb(slots, user_id, lang)
    )


@router.callback_query(F.data == "my_slots")
async def show_my_slots(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.clear()
    await _render_my_slots(callback, lang)
    await callback.answer()


# ----------------------------------------------------------------- Bekor qilish


@router.callback_query(F.data.startswith("slot_cancel_"))
async def cancel_slot(callback: CallbackQuery, lang: str = "uz"):
    slot_id = callback.data.replace("slot_cancel_", "", 1)
    mentor_id = callback.from_user.id

    async with get_db() as db:
        result = await SlotService(db).cancel_slot(slot_id, mentor_id)

    if result is None:
        await callback.answer(t("slot_cancel_failed", lang), show_alert=True)
        return

    if result["refunded_mentee_id"] is not None:
        async with get_db() as db:
            mentee = await UserRepository(db).get_by_id(result["refunded_mentee_id"])
        if mentee is not None:
            await NotificationService(callback.bot).send(
                mentee.id,
                t(
                    "slot_cancelled_mentee",
                    mentee.language,
                    direction=direction_label(result["direction"]),
                    time=fmt_range(result["start_time"], result["end_time"]),
                ),
            )

    await callback.answer(t("slot_cancelled_ok", lang), show_alert=True)
    await _render_my_slots(callback, lang)


# ----------------------------------------------------------------- Tahrirlash


def _edit_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("slot_edit_direction_btn", lang),
                    callback_data="editfield_direction",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("slot_edit_time_btn", lang),
                    callback_data="editfield_time",
                )
            ],
            [_back_button(lang, "my_slots")],
        ]
    )


@router.callback_query(F.data.startswith("slotedit_"))
async def edit_slot_start(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    slot_id = callback.data.replace("slotedit_", "", 1)

    async with get_db() as db:
        slot = await SlotService(db).get_slot_by_id(slot_id)

    if slot is None or slot.mentor_id != callback.from_user.id:
        await callback.answer(t("slot_edit_failed", lang), show_alert=True)
        return
    if slot.status != "open":
        await callback.answer(t("slot_edit_not_open", lang), show_alert=True)
        return

    await state.update_data(edit_slot_id=slot_id)
    await state.set_state(EditStates.choosing_field)
    await callback.message.edit_text(
        t(
            "slot_edit_title",
            lang,
            direction=direction_label(slot.direction),
            time=fmt_range(slot.start_time, slot.end_time),
        ),
        reply_markup=_edit_menu_kb(lang),
    )
    await callback.answer()


@router.callback_query(EditStates.choosing_field, F.data == "editfield_direction")
async def edit_choose_direction(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.set_state(EditStates.selecting_direction)
    await callback.message.edit_text(
        t("slot_edit_select_direction", lang),
        reply_markup=get_directions_single_kb(prefix="edir_", back_cb="my_slots", language=lang),
    )
    await callback.answer()


@router.callback_query(EditStates.selecting_direction, F.data.startswith("edir_"))
async def edit_apply_direction(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    direction = callback.data.replace("edir_", "", 1)
    data = await state.get_data()
    slot_id = data["edit_slot_id"]

    async with get_db() as db:
        slot = await SlotService(db).update_slot(
            slot_id, callback.from_user.id, direction=direction
        )

    await state.clear()
    if slot is None:
        await callback.answer(t("slot_edit_not_open", lang), show_alert=True)
        await _render_my_slots(callback, lang)
        return
    await callback.message.edit_text(
        t(
            "slot_edit_ok",
            lang,
            direction=direction_label(slot.direction),
            time=fmt_range(slot.start_time, slot.end_time),
        ),
        reply_markup=get_main_menu_kb(lang),
    )
    await callback.answer()


@router.callback_query(EditStates.choosing_field, F.data == "editfield_time")
async def edit_choose_time(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.set_state(EditStates.selecting_date)
    now = now_local()
    await callback.message.edit_text(
        t("slot_edit_select_date", lang),
        reply_markup=get_calendar_kb(now.year, now.month, now=now),
    )
    await callback.answer()


@router.callback_query(EditStates.selecting_date, F.data.startswith("calnav_"))
async def edit_calendar_nav(callback: CallbackQuery, lang: str = "uz"):
    _, year, month = callback.data.split("_")
    await callback.message.edit_reply_markup(reply_markup=get_calendar_kb(int(year), int(month)))
    await callback.answer()


@router.callback_query(EditStates.selecting_date, F.data.startswith("calday_"))
async def edit_select_date(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    target_date = date.fromisoformat(callback.data.replace("calday_", "", 1))
    await state.update_data(edit_date=target_date.isoformat())
    await state.set_state(EditStates.selecting_start_time)
    await callback.message.edit_text(
        t("slot_edit_select_start", lang),
        reply_markup=get_mentor_start_kb(target_date),
    )
    await callback.answer()


@router.callback_query(EditStates.selecting_start_time, F.data.startswith("mstart_"))
async def edit_select_start(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    iso = callback.data.replace("mstart_", "", 1)
    start_time = datetime.fromisoformat(iso)
    await state.update_data(edit_start=iso)
    await state.set_state(EditStates.selecting_end_time)
    await callback.message.edit_text(
        t("slot_edit_select_end", lang, start=fmt_datetime(start_time)),
        reply_markup=get_mentor_end_kb(start_time),
    )
    await callback.answer()


@router.callback_query(EditStates.selecting_end_time, F.data.startswith("mend_"))
async def edit_select_end(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    end_time = datetime.fromisoformat(callback.data.replace("mend_", "", 1))
    data = await state.get_data()
    slot_id = data["edit_slot_id"]
    start_time = datetime.fromisoformat(data["edit_start"])

    async with get_db() as db:
        try:
            slot = await SlotService(db).update_slot(
                slot_id,
                callback.from_user.id,
                start_time=start_time,
                end_time=end_time,
            )
        except SlotValidationError as exc:
            await state.clear()
            await callback.message.edit_text(
                t("slot_invalid_time", lang, error=str(exc)),
                reply_markup=get_main_menu_kb(lang),
            )
            await callback.answer()
            return

    await state.clear()
    if slot is None:
        await callback.answer(t("slot_edit_not_open", lang), show_alert=True)
        await _render_my_slots(callback, lang)
        return
    await callback.message.edit_text(
        t(
            "slot_edit_ok",
            lang,
            direction=direction_label(slot.direction),
            time=fmt_range(slot.start_time, slot.end_time),
        ),
        reply_markup=get_main_menu_kb(lang),
    )
    await callback.answer()


# ----------------------------------------------------------------- Reyting


@router.callback_query(F.data == "leaderboard")
async def show_leaderboard(callback: CallbackQuery, lang: str = "uz"):
    async with get_db() as db:
        top = await UserRepository(db).get_leaderboard(limit=10)

    if not top:
        await callback.message.edit_text(
            t("leaderboard_empty", lang), reply_markup=get_main_menu_kb(lang)
        )
        await callback.answer()
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = [t("leaderboard_title", lang), ""]
    for i, u in enumerate(top):
        prefix = medals[i] if i < len(medals) else f"{i + 1}."
        name = ("@" + u.username) if u.username else (u.nickname or u.school21_login)
        lines.append(f"{prefix} {name} — {u.xp} XP (L{u.level}, 🎓 {u.total_taught})")
    await callback.message.edit_text("\n".join(lines), reply_markup=get_main_menu_kb(lang))
    await callback.answer()
