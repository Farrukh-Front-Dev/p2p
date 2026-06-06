"""Eslatma va sessiya boshlash scheduleri (APScheduler)."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..config import settings
from ..database.models.slot import Slot
from ..repositories.slot_repo import SlotRepository
from ..repositories.user_repo import UserRepository
from ..utils.format_utils import display_name
from ..utils.i18n import t
from ..utils.time_utils import fmt_range, now_local
from .chat_service import get_chat_service
from .notification_service import NotificationService
from .session_service import SessionService

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, bot: Bot, sessionmaker=None):
        self.bot = bot
        self.notifier = NotificationService(bot)
        self.chat_service = get_chat_service(bot)
        # Testda almashtirish uchun sessionmaker'ni in'ektsiya qilish mumkin
        if sessionmaker is None:
            from ..database.session import get_sessionmaker

            sessionmaker = get_sessionmaker()
        self._sessionmaker = sessionmaker

        # Memory jobstore: yagona takrorlanuvchi `check_slots` vazifasi har
        # ishga tushishda qayta qo'shiladi; slot holatlari PostgreSQL'da
        # saqlanadi, shuning uchun jobstore'ni Redis'da saqlash shart emas
        # (bog'langan metodni pickle qilib bo'lmaydi).
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self.scheduler.add_job(
            self.check_slots,
            "interval",
            minutes=1,
            id="check_slots",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info("Scheduler started")

    async def check_slots(self) -> None:
        """Har 1 daqiqada chaqiriladi: eslatma va sessiya boshlash."""
        try:
            await self.process_reminders()
        except Exception:
            logger.exception("process_reminders failed")
        try:
            await self.process_starts()
        except Exception:
            logger.exception("process_starts failed")

    async def process_reminders(self, now: datetime | None = None) -> int:
        """Eslatma yuborilishi kerak bo'lgan slotlar uchun reveal yuboradi."""
        now = now or now_local()
        threshold = now + timedelta(minutes=settings.REMINDER_MINUTES)
        sent = 0
        async with self._sessionmaker() as db:
            slot_repo = SlotRepository(db)
            slots = await slot_repo.get_slots_for_reminder(now, threshold)
            for slot in slots:
                # Atomik belgilash: faqat bittasi reminder yuboradi (Property 7)
                marked = await slot_repo.mark_reminder_sent(slot.id)
                if not marked:
                    continue
                await db.commit()
                await self._send_reminder(db, slot)
                sent += 1
        return sent

    async def _send_reminder(self, db, slot: Slot) -> None:
        user_repo = UserRepository(db)
        mentor = await user_repo.get_by_id(slot.mentor_id)
        mentee = await user_repo.get_by_id(slot.mentee_id)
        time_str = fmt_range(slot.start_time, slot.end_time)

        if mentor is not None and mentee is not None:
            await self.notifier.send(
                mentor.id,
                t(
                    "reminder_mentor",
                    mentor.language,
                    direction=slot.direction,
                    time=time_str,
                    peer=display_name(mentee),
                ),
            )
            await self.notifier.send(
                mentee.id,
                t(
                    "reminder_mentee",
                    mentee.language,
                    direction=slot.direction,
                    time=time_str,
                    peer=display_name(mentor),
                ),
            )

    async def process_starts(self, now: datetime | None = None) -> int:
        """Boshlanish vaqti kelgan slotlar uchun sessiya ochadi."""
        now = now or now_local()
        started = 0
        async with self._sessionmaker() as db:
            slot_repo = SlotRepository(db)
            session_service = SessionService(db)
            slots = await slot_repo.get_slots_to_start(now)
            for slot in slots:
                try:
                    session = await session_service.create_session(slot)
                    await db.commit()
                    chat_ref = await self.chat_service.open_channel(session)
                    await self._notify_start(db, slot)
                    logger.info("Session %s started (chat=%s)", session.id, chat_ref)
                    started += 1
                except Exception:
                    logger.exception("Failed to start session for slot %s", slot.id)
                    await db.rollback()
        return started

    async def _notify_start(self, db, slot: Slot) -> None:
        user_repo = UserRepository(db)
        mentor = await user_repo.get_by_id(slot.mentor_id)
        mentee = await user_repo.get_by_id(slot.mentee_id)
        for user in (mentor, mentee):
            if user is not None:
                await self.notifier.send(
                    user.id,
                    t("session_started", user.language, direction=slot.direction),
                )
