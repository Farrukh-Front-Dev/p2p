"""Xabar yuborish servisi (i18n + xatolarni yutish)."""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError

from ..utils.i18n import t

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send(
        self,
        user_id: int,
        text: str,
        reply_markup=None,
    ) -> bool:
        """Tayyor matnli xabar yuboradi. Bot bloklangan bo'lsa xatoni yutadi."""
        try:
            await self.bot.send_message(user_id, text, reply_markup=reply_markup)
            return True
        except TelegramForbiddenError:
            logger.info("User %s blocked the bot; skipping message", user_id)
            return False
        except TelegramAPIError as exc:
            logger.warning("Failed to send message to %s: %s", user_id, exc)
            return False

    async def send_key(
        self,
        user_id: int,
        key: str,
        lang: str = "uz",
        reply_markup=None,
        **kwargs,
    ) -> bool:
        """i18n kalit bo'yicha xabar yuboradi."""
        return await self.send(user_id, t(key, lang, **kwargs), reply_markup)
