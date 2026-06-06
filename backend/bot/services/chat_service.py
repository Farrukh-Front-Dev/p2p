"""ChatService abstraksiyasi va implementatsiyalari.

MVP: RelayChatService (bot xabarlarni ikki tomon orasida uzatadi).
Kelajak: UserBotChatService (Telethon/Pyrogram orqali haqiqiy guruh).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from aiogram import Bot
from aiogram.types import Message

from ..config import settings
from ..database.models.session import Session
from .redis_client import get_redis

logger = logging.getLogger(__name__)


def _relay_key(session_id: object, suffix: str) -> str:
    return f"relay:{session_id}:{suffix}"


class ChatService(ABC):
    """Aloqa kanali abstraksiyasi."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @abstractmethod
    async def open_channel(self, session: Session) -> str:
        """Aloqa kanalini ochadi, chat_ref (relay id yoki group_id) qaytaradi."""

    @abstractmethod
    async def relay(self, session_id: str, from_user_id: int, message: Message) -> bool:
        """Xabarni qarama-qarshi tomonga yetkazadi. True = yetkazildi."""

    @abstractmethod
    async def close_channel(self, session: Session) -> None:
        """Kanalni yopadi/tozalaydi."""

    @abstractmethod
    async def get_peer(self, session_id: str, from_user_id: int) -> int | None:
        """from_user_id ga juft bo'lgan tomon ID sini qaytaradi (yoki None)."""


class RelayChatService(ChatService):
    """Bot relay: har bir tomon bot bilan yozadi, bot ikkinchisiga uzatadi."""

    async def open_channel(self, session: Session) -> str:
        redis = get_redis()
        sid = str(session.id)
        mapping = {
            _relay_key(sid, "mentor"): str(session.mentor_id),
            _relay_key(sid, "mentee"): str(session.mentee_id),
            _relay_key(sid, "active"): "1",
        }
        await redis.mset(mapping)
        # Foydalanuvchi -> sessiya teskari indeksi (relay uchun)
        await redis.set(f"relay:user:{session.mentor_id}", sid)
        await redis.set(f"relay:user:{session.mentee_id}", sid)
        return sid

    async def get_peer(self, session_id: str, from_user_id: int) -> int | None:
        redis = get_redis()
        mentor = await redis.get(_relay_key(session_id, "mentor"))
        mentee = await redis.get(_relay_key(session_id, "mentee"))
        if mentor is None or mentee is None:
            return None
        if str(from_user_id) == mentor:
            return int(mentee)
        if str(from_user_id) == mentee:
            return int(mentor)
        return None

    async def get_session_for_user(self, user_id: int) -> str | None:
        """Foydalanuvchining faol relay sessiyasini qaytaradi."""
        redis = get_redis()
        return await redis.get(f"relay:user:{user_id}")

    async def relay(self, session_id: str, from_user_id: int, message: Message) -> bool:
        redis = get_redis()
        if await redis.get(_relay_key(session_id, "active")) != "1":
            return False
        peer_id = await self.get_peer(session_id, from_user_id)
        if peer_id is None:
            return False
        try:
            # copy_message matn, rasm, fayl, ovozli va h.k. uchun universal ishlaydi
            await self.bot.copy_message(
                chat_id=peer_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
            return True
        except Exception as exc:  # TelegramForbiddenError va boshqalar
            logger.warning("Relay error (peer=%s): %s", peer_id, exc)
            return False

    async def close_channel(self, session: Session) -> None:
        redis = get_redis()
        sid = str(session.id)
        await redis.delete(
            _relay_key(sid, "mentor"),
            _relay_key(sid, "mentee"),
            _relay_key(sid, "active"),
            f"relay:user:{session.mentor_id}",
            f"relay:user:{session.mentee_id}",
        )


class UserBotChatService(ChatService):
    """Kelajakdagi implementatsiya: Telethon/Pyrogram orqali haqiqiy guruh.

    Hozircha amalga oshirilmagan — CHAT_BACKEND=relay standart.
    """

    async def open_channel(self, session: Session) -> str:
        raise NotImplementedError(
            "UserBotChatService hali amalga oshirilmagan. CHAT_BACKEND=relay ishlating."
        )

    async def relay(self, session_id: str, from_user_id: int, message: Message) -> bool:
        # Haqiqiy guruhda relay kerak emas (Telegram o'zi yetkazadi)
        return False

    async def get_peer(self, session_id: str, from_user_id: int) -> int | None:
        return None

    async def close_channel(self, session: Session) -> None:
        raise NotImplementedError


def get_chat_service(bot: Bot) -> ChatService:
    """CHAT_BACKEND setting bo'yicha mos ChatService yaratadi."""
    if settings.CHAT_BACKEND == "userbot":
        return UserBotChatService(bot)
    return RelayChatService(bot)
