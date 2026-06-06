"""Anti-spam throttling middleware (Redis token-bucket)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from ..services.redis_client import get_redis


class ThrottlingMiddleware(BaseMiddleware):
    """Har bir foydalanuvchi uchun `limit` so'rov / `window` soniya."""

    def __init__(self, limit: int = 5, window: int = 2):
        self.limit = limit
        self.window = window

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = data.get("event_from_user")
        if tg_user is None:
            return await handler(event, data)

        try:
            redis = get_redis()
            key = f"throttle:{tg_user.id}"
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, self.window)
            if count > self.limit:
                # Limit oshib ketdi — so'rovni rad etamiz
                if isinstance(event, CallbackQuery):
                    await event.answer("⏳", show_alert=False)
                elif isinstance(event, Message):
                    pass  # jim tashlab yuboramiz (spamni kuchaytirmaslik uchun)
                return None
        except Exception:
            # Redis ishlamasa, throttling'ni o'tkazib yuboramiz (fail-open)
            return await handler(event, data)

        return await handler(event, data)
