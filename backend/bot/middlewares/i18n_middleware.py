"""i18n middleware: foydalanuvchi tilini aniqlab, tarjima funksiyasini beradi."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from ..utils.i18n import DEFAULT_LANG, get_translator


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("user")
        lang = getattr(user, "language", None) or DEFAULT_LANG
        data["lang"] = lang
        data["_"] = get_translator(lang)
        return await handler(event, data)
