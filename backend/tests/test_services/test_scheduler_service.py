"""SchedulerService testlari (Property 6, 7)."""

from __future__ import annotations

from datetime import timedelta

import fakeredis.aioredis
import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.database import models  # noqa: F401
from bot.database.base import Base
from bot.database.models.enums import SlotStatus
from bot.database.models.slot import Slot
from bot.database.models.user import User
from bot.services import redis_client
from bot.services.scheduler_service import SchedulerService
from bot.utils.time_utils import now_local


class FakeBot:
    def __init__(self):
        self.messages: list[dict] = []

    async def send_message(self, chat_id, text, reply_markup=None):
        self.messages.append({"chat_id": chat_id, "text": text})

    async def copy_message(self, **kwargs):
        pass


@pytest.fixture(autouse=True)
def _fake_redis():
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    redis_client.set_redis(client)
    yield client
    redis_client._redis = None


async def _maker():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def _seed_booked_slot(maker, start_in_minutes=10):
    async with maker() as db:
        db.add_all(
            [
                User(id=10, username="mentor_u", school21_login="m", language="uz"),
                User(id=11, username="mentee_u", school21_login="me", language="uz"),
            ]
        )
        await db.flush()
        now = now_local()
        slot = Slot(
            mentor_id=10,
            mentee_id=11,
            direction="python",
            start_time=now + timedelta(minutes=start_in_minutes),
            end_time=now + timedelta(minutes=start_in_minutes + 60),
            status=SlotStatus.BOOKED.value,
        )
        db.add(slot)
        await db.commit()
        return slot.id


@pytest.mark.asyncio
async def test_reminder_sent_once():
    """Property 7: eslatma ko'pi bilan bir marta yuboriladi."""
    engine, maker = await _maker()
    try:
        await _seed_booked_slot(maker, start_in_minutes=10)
        sched = SchedulerService(FakeBot(), sessionmaker=maker)

        first = await sched.process_reminders()
        second = await sched.process_reminders()

        assert first == 1
        assert second == 0  # ikkinchi marta yubormaydi

        async with maker() as db:
            from sqlalchemy import select

            slot = (await db.execute(select(Slot))).scalar_one()
            assert slot.reminder_sent is True
            assert slot.reveal_sent is True
            assert slot.status == SlotStatus.REMINDED.value
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_reminder_reveals_identities():
    """Reveal: eslatmada sherikning nomi ko'rsatiladi."""
    engine, maker = await _maker()
    try:
        await _seed_booked_slot(maker, start_in_minutes=10)
        bot = FakeBot()
        sched = SchedulerService(bot, sessionmaker=maker)
        await sched.process_reminders()

        # Mentorga yuborilgan xabarda mentee username bo'lishi kerak
        mentor_msg = next(m for m in bot.messages if m["chat_id"] == 10)
        mentee_msg = next(m for m in bot.messages if m["chat_id"] == 11)
        assert "@mentee_u" in mentor_msg["text"]
        assert "@mentor_u" in mentee_msg["text"]
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_no_reminder_before_threshold():
    """Property 6: vaqt yetib kelmagan slot uchun eslatma (reveal) yuborilmaydi."""
    engine, maker = await _maker()
    try:
        # 60 daqiqadan keyin boshlanadi, threshold = 15 daqiqa
        await _seed_booked_slot(maker, start_in_minutes=60)
        bot = FakeBot()
        sched = SchedulerService(bot, sessionmaker=maker)
        sent = await sched.process_reminders()

        assert sent == 0
        assert bot.messages == []  # hech qanday reveal yuborilmadi

        async with maker() as db:
            from sqlalchemy import select

            slot = (await db.execute(select(Slot))).scalar_one()
            assert slot.reminder_sent is False
            assert slot.reveal_sent is False
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_session_start_creates_active_session():
    """process_starts: reminded slot active sessiyaga aylanadi."""
    engine, maker = await _maker()
    try:
        # reminded holatda, vaqti kelgan slot
        async with maker() as db:
            db.add_all(
                [
                    User(id=10, username="m_u", school21_login="m", language="uz"),
                    User(id=11, username="me_u", school21_login="me", language="uz"),
                ]
            )
            await db.flush()
            now = now_local()
            slot = Slot(
                mentor_id=10,
                mentee_id=11,
                direction="python",
                start_time=now - timedelta(minutes=1),
                end_time=now + timedelta(minutes=59),
                status=SlotStatus.REMINDED.value,
                reminder_sent=True,
                reveal_sent=True,
            )
            db.add(slot)
            await db.commit()
            slot_id = slot.id

        bot = FakeBot()
        sched = SchedulerService(bot, sessionmaker=maker)
        started = await sched.process_starts()
        assert started == 1

        async with maker() as db:
            from sqlalchemy import select

            from bot.database.models.session import Session

            slot = await db.get(Slot, slot_id)
            assert slot.status == SlotStatus.ACTIVE.value
            sess = (await db.execute(select(Session))).scalar_one()
            assert sess.mentor_id == 10
            assert sess.mentee_id == 11
        # relay kanali ochilgan (foydalanuvchi indeks mavjud)
        from bot.services.chat_service import RelayChatService

        relay = RelayChatService(bot)
        assert await relay.get_session_for_user(10) is not None
    finally:
        await engine.dispose()
