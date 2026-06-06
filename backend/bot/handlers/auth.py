"""start va auth (ro'yxatdan o'tish) handlerlari."""

from __future__ import annotations

import contextlib
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..database.session import get_db
from ..keyboards.directions_kb import get_directions_kb
from ..keyboards.main_menu import get_main_menu_kb
from ..repositories.user_repo import UserRepository
from ..services.school21_api import school21_api
from ..states.auth_states import AuthStates
from ..utils.i18n import t

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user=None, lang: str = "uz"):
    await state.clear()
    if user is not None and user.is_active:
        await message.answer(
            t("welcome_back", user.language, name=user.nickname or user.username or ""),
            reply_markup=get_main_menu_kb(user.language),
        )
        return

    await state.set_state(AuthStates.waiting_login)
    await message.answer(t("welcome", lang) + "\n\n" + t("enter_login", lang))


@router.message(AuthStates.waiting_login)
async def process_login(message: Message, state: FSMContext, lang: str = "uz"):
    login = (message.text or "").strip()
    if len(login) < 2 or len(login) > 64:
        await message.answer(t("login_invalid", lang))
        return

    await state.update_data(school21_login=login)
    await state.set_state(AuthStates.waiting_password)
    await message.answer(t("enter_password", lang))


@router.message(AuthStates.waiting_password)
async def process_password(message: Message, state: FSMContext, lang: str = "uz"):
    password = (message.text or "").strip()
    # Parolni darhol o'chirish (xavfsizlik)
    with contextlib.suppress(Exception):
        await message.delete()

    data = await state.get_data()
    login = data.get("school21_login", "")
    wait_msg = await message.answer(t("auth_checking", lang))

    token_data = await school21_api.authenticate(login, password)
    if not token_data:
        await wait_msg.edit_text(t("auth_failed", lang))
        await state.clear()
        return

    access_token = token_data["access_token"]
    profile = await school21_api.get_profile(login, access_token) or {}
    suggested = await school21_api.suggest_directions(login, access_token)

    await state.update_data(
        profile=profile,
        s21_login=profile.get("login", login),
        selected_directions=suggested[:5],
    )
    await state.set_state(AuthStates.selecting_directions)
    await wait_msg.edit_text(
        t("auth_success", lang) + "\n\n" + t("select_directions", lang),
        reply_markup=get_directions_kb(selected=suggested[:5], language=lang),
    )


@router.callback_query(AuthStates.selecting_directions, F.data.startswith("dir_"))
async def toggle_direction(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    payload = callback.data.replace("dir_", "", 1)
    data = await state.get_data()
    selected: list[str] = data.get("selected_directions", [])

    if payload == "confirm":
        if not selected:
            await callback.answer(t("min_one_direction", lang), show_alert=True)
            return
        await _finish_registration(callback, state, lang)
        return

    if payload in selected:
        selected.remove(payload)
    else:
        if len(selected) >= 5:
            await callback.answer(t("max_directions", lang), show_alert=True)
            return
        selected.append(payload)

    await state.update_data(selected_directions=selected)
    with contextlib.suppress(Exception):
        await callback.message.edit_reply_markup(
            reply_markup=get_directions_kb(selected=selected, language=lang)
        )
    await callback.answer()


async def _finish_registration(callback: CallbackQuery, state: FSMContext, lang: str):
    data = await state.get_data()
    profile = data.get("profile", {})
    directions = data.get("selected_directions", [])
    login = data.get("s21_login") or data.get("school21_login")
    tg_user = callback.from_user

    async with get_db() as db:
        repo = UserRepository(db)
        await repo.create_or_update(
            user_id=tg_user.id,
            username=tg_user.username,
            school21_login=login,
            nickname=profile.get("login", login),
            avatar_url=None,
            directions=directions,
            language=lang,
            level=1,
            xp=0,
        )

    await state.clear()
    await callback.message.edit_text(t("registered", lang, count=len(directions), coins=5))
    await callback.message.answer(t("welcome", lang), reply_markup=get_main_menu_kb(lang))
    await callback.answer()
