"""Admin panel handlerlari (/admin, /bonus, /broadcast)."""

from __future__ import annotations

import asyncio
import logging

from aiogram import BaseMiddleware, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, TelegramObject

from ..config import settings
from ..database.session import get_db
from ..repositories.stats_repo import StatsRepository
from ..repositories.user_repo import UserRepository
from ..services.coin_service import CoinService
from ..services.notification_service import NotificationService
from ..utils.i18n import t

logger = logging.getLogger(__name__)
router = Router()


class AdminFilterMiddleware(BaseMiddleware):
    """Faqat ADMIN_IDS dagi foydalanuvchilarga ruxsat beradi."""

    async def __call__(self, handler, event: TelegramObject, data: dict):
        tg_user = data.get("event_from_user")
        if tg_user is None or tg_user.id not in settings.ADMIN_IDS:
            if isinstance(event, Message):
                lang = data.get("lang", "uz")
                await event.answer(t("admin_only", lang))
            return None
        return await handler(event, data)


# Bu router'dagi barcha message handlerlarga admin filtri
router.message.middleware(AdminFilterMiddleware())


@router.message(Command("admin"))
async def cmd_admin_stats(message: Message, lang: str = "uz"):
    async with get_db() as db:
        stats = await StatsRepository(db).gather()
    await message.answer(t("admin_stats", lang, **stats))


@router.message(Command("bonus"))
async def cmd_bonus(message: Message, command: CommandObject, lang: str = "uz"):
    args = (command.args or "").split()
    if len(args) != 2:
        await message.answer(t("admin_bonus_usage", lang))
        return
    try:
        target_id = int(args[0])
        amount = int(args[1])
    except ValueError:
        await message.answer(t("admin_bonus_usage", lang))
        return

    async with get_db() as db:
        urepo = UserRepository(db)
        user = await urepo.get_by_id(target_id)
        if user is None:
            await message.answer(t("admin_bonus_user_not_found", lang, user_id=target_id))
            return
        coin_service = CoinService(db)
        await coin_service.add_bonus(target_id, amount, description="admin bonus")

    await message.answer(t("admin_bonus_ok", lang, user_id=target_id, amount=amount))


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, command: CommandObject, lang: str = "uz"):
    text = (command.args or "").strip()
    if not text:
        await message.answer(t("admin_broadcast_usage", lang))
        return

    async with get_db() as db:
        user_ids = await StatsRepository(db).all_user_ids()

    notifier = NotificationService(message.bot)
    sent = 0
    for uid in user_ids:
        ok = await notifier.send(uid, text)
        if ok:
            sent += 1
        await asyncio.sleep(0.05)  # flood-limitdan saqlanish

    await message.answer(t("admin_broadcast_done", lang, count=sent))
