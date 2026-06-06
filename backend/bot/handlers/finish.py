"""Sessiyani yakunlash (/finish) handleri."""

from __future__ import annotations

import contextlib

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..config import settings
from ..database.models.enums import SessionStatus
from ..database.session import get_db
from ..keyboards.confirm_kb import get_confirm_kb
from ..keyboards.main_menu import get_main_menu_kb
from ..repositories.user_repo import UserRepository
from ..services.chat_service import get_chat_service
from ..services.notification_service import NotificationService
from ..services.session_service import SessionService
from ..states.finish_states import FinishStates
from ..utils.i18n import t

router = Router()


@router.message(Command("finish"))
async def cmd_finish(message: Message, state: FSMContext, lang: str = "uz"):
    async with get_db() as db:
        service = SessionService(db)
        session = await service.get_active_session_by_user(message.from_user.id)

    if session is None:
        await message.answer(t("finish_no_session", lang))
        return

    await state.update_data(session_id=str(session.id))
    await state.set_state(FinishStates.confirming_finish)
    await message.answer(
        t("finish_confirm", lang),
        reply_markup=get_confirm_kb("finish_session", lang),
    )


@router.callback_query(FinishStates.confirming_finish, F.data == "confirm_finish_session")
async def finish_confirm(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.set_state(FinishStates.writing_comment)
    await callback.message.edit_text(t("finish_write_comment", lang))
    await callback.answer()


@router.callback_query(F.data == "cancel_finish_session")
async def finish_cancel(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.clear()
    await callback.message.edit_text(t("welcome", lang), reply_markup=get_main_menu_kb(lang))
    await callback.answer()


@router.message(FinishStates.writing_comment)
async def finish_comment(message: Message, state: FSMContext, lang: str = "uz"):
    comment = (message.text or "").strip()
    if len(comment) < 10:
        await message.answer(t("finish_comment_short", lang))
        return

    data = await state.get_data()
    session_id = data.get("session_id")
    user_id = message.from_user.id

    async with get_db() as db:
        service = SessionService(db)
        session = await service.submit_finish(session_id, user_id, comment)

    if session is None:
        await state.clear()
        await message.answer(t("finish_no_session", lang))
        return

    await state.clear()

    if session.status == SessionStatus.FINISHED.value:
        # Ikkala tomon tasdiqladi — relay yopiladi va ikkalasiga mukofot xabari
        await _notify_finish(message, session)
    else:
        await message.answer(t("finish_waiting_peer", lang), reply_markup=get_main_menu_kb(lang))


async def _notify_finish(message: Message, session) -> None:
    """Sessiya yakunlanganda relay kanalini yopish va ikki tomonga xabar."""
    notifier = NotificationService(message.bot)
    chat_service = get_chat_service(message.bot)
    with contextlib.suppress(NotImplementedError):
        await chat_service.close_channel(session)

    async with get_db() as db:
        repo = UserRepository(db)
        mentor = await repo.get_by_id(session.mentor_id)
        mentee = await repo.get_by_id(session.mentee_id)

    if mentor is not None:
        await notifier.send(
            mentor.id,
            t(
                "finish_done_mentor",
                mentor.language,
                coins=settings.COIN_PER_SESSION,
                xp=settings.XP_PER_SESSION,
            ),
            reply_markup=get_main_menu_kb(mentor.language),
        )
    if mentee is not None:
        await notifier.send(
            mentee.id,
            t(
                "finish_done_mentee",
                mentee.language,
                xp=settings.XP_PER_SESSION // 2,
            ),
            reply_markup=get_main_menu_kb(mentee.language),
        )
