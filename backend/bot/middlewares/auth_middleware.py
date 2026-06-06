"""Auth middleware: foydalanuvchini yuklaydi va ruxsatni tekshiradi."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, TelegramObject

from ..database.session import get_db
from ..repositories.user_repo import UserRepository

# Ro'yxatdan o'tmaganlarga ruxsat etilgan buyruqlar
_ALLOWED_COMMANDS = {"/start"}


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = data.get("event_from_user")
        if tg_user is None:
            return await handler(event, data)

        async with get_db() as db:
            repo = UserRepository(db)
            user = await repo.get_by_id(tg_user.id)
            data["user"] = user

            if user is not None and user.is_active:
                return await handler(event, data)

            # Ro'yxatdan o'tmagan: faqat /start yoki auth FSM holatiga ruxsat
            state: FSMContext | None = data.get("state")
            current_state = await state.get_state() if state else None

            if current_state is not None and current_state.startswith("AuthStates"):
                return await handler(event, data)

            if isinstance(event, Message) and event.text:
                if event.text.strip().split()[0] in _ALLOWED_COMMANDS:
                    return await handler(event, data)
                await event.answer("Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting.")
                return None

            if isinstance(event, CallbackQuery):
                await event.answer("Iltimos, /start orqali ro'yxatdan o'ting.", show_alert=True)
                return None

            return None
