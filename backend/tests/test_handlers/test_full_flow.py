"""To'liq oqim integratsion testi (servis qatlami orqali).

Auth -> teach -> learn -> reminder -> session start -> finish.
Tashqi xizmatlar: SQLite (in-memory), fakeredis, respx (School21).
"""

from __future__ import annotations

from datetime import timedelta

import fakeredis.aioredis
import httpx
import pytest
import respx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.config import settings
from bot.database import models  # noqa: F401
from bot.database.base import Base
from bot.database.models.enums import SessionStatus, SlotStatus
from bot.database.models.slot import Slot
from bot.database.models.transaction import Transaction
from bot.database.models.user import User
from bot.repositories.user_repo import UserRepository
from bot.services import redis_client
from bot.services.coin_service import CoinService
from bot.services.scheduler_service import SchedulerService
from bot.services.school21_api import School21Client
from bot.services.session_service import SessionService
from bot.services.slot_service import SlotService
from bot.utils.time_utils import now_local


class FakeBot:
    def __init__(self):
        self.sent: list[dict] = []
        self.copied: list[dict] = []

    async def send_message(self, chat_id, text, reply_markup=None):
        self.sent.append({"chat_id": chat_id, "text": text})

    async def copy_message(self, chat_id, from_chat_id, message_id):
        self.copied.append({"chat_id": chat_id, "message_id": message_id})


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


@pytest.mark.asyncio
@respx.mock
async def test_full_lifecycle():
    # --- School 21 mock (auth + profil + skills) ---
    respx.post(settings.S21_TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "tok", "expires_in": 36000})
    )
    respx.get(f"{settings.S21_API_URL}/participants/mentor21").mock(
        return_value=httpx.Response(200, json={"login": "mentor21", "level": 5, "expValue": 1200})
    )
    respx.get(f"{settings.S21_API_URL}/participants/mentor21/skills").mock(
        return_value=httpx.Response(200, json={"skills": [{"name": "Python", "points": 900}]})
    )

    engine, maker = await _maker()
    try:
        # === 1. AUTH: ikki foydalanuvchi ro'yxatdan o'tadi ===
        client = School21Client()
        token = await client.authenticate("mentor21", "pw")
        assert token is not None
        profile = await client.get_profile("mentor21", token["access_token"])
        await client.close()

        async with maker() as db:
            repo = UserRepository(db)
            await repo.create_or_update(
                user_id=1,
                username="mentor_tg",
                school21_login="mentor21",
                nickname=profile["login"],
                directions=["python"],
                level=1,
                xp=0,
            )
            await repo.create_or_update(
                user_id=2,
                username="mentee_tg",
                school21_login="mentee21",
                nickname="mentee21",
                directions=["python"],
            )
            await db.commit()

        # === 2. TEACH: mentor slot ochadi ===
        now = now_local()
        async with maker() as db:
            slot_service = SlotService(db)
            slot = await slot_service.create_slot(
                mentor_id=1,
                direction="python",
                start_time=now + timedelta(minutes=10),
                end_time=now + timedelta(minutes=70),
            )
            await db.commit()
            slot_id = slot.id

        # === 3. LEARN: mentee anonim ko'radi va band qiladi (-1 coin) ===
        async with maker() as db:
            slot_service = SlotService(db)
            available = await slot_service.get_available_slots("python", exclude_user_id=2)
            assert len(available) == 1
            # Anonimlik: ro'yxatda mentor_id oshkor bo'lmaydi (faqat slot ko'rsatiladi)

            booked = await slot_service.book_slot(
                slot_id,
                mentee_id=2,
                booking_start=available[0].start_time,
                booking_end=available[0].end_time,
            )
            assert booked is True
            coin_service = CoinService(db)
            assert await coin_service.deduct(2, 1, reason="spend_learn", slot_id=slot_id)
            await db.commit()

        async with maker() as db:
            mentee = await db.get(User, 2)
            assert mentee.coins == 4  # 5 - 1

        # === 4. REMINDER: 15 daqiqa oldin reveal ===
        bot = FakeBot()
        sched = SchedulerService(bot, sessionmaker=maker)
        sent = await sched.process_reminders(now=now)
        assert sent == 1
        async with maker() as db:
            slot = await db.get(Slot, slot_id)
            assert slot.status == SlotStatus.REMINDED.value
            assert slot.reveal_sent is True

        # === 5. SESSION START: vaqt kelganda sessiya ochiladi ===
        start_moment = now + timedelta(minutes=11)
        started = await sched.process_starts(now=start_moment)
        assert started == 1
        async with maker() as db:
            slot = await db.get(Slot, slot_id)
            assert slot.status == SlotStatus.ACTIVE.value

        # relay kanali ochilgan — xabar uzatish ishlaydi
        from types import SimpleNamespace

        from bot.services.chat_service import RelayChatService

        relay = RelayChatService(bot)
        sid = await relay.get_session_for_user(1)
        assert sid is not None
        msg = SimpleNamespace(chat=SimpleNamespace(id=1), message_id=7)
        assert await relay.relay(sid, from_user_id=1, message=msg) is True
        assert bot.copied[-1]["chat_id"] == 2  # mentor -> mentee

        # === 6. FINISH: ikki tomon tasdiqlaydi -> coin/XP ===
        async with maker() as db:
            svc = SessionService(db)
            sess = await svc.get_active_session_by_user(1)
            await svc.submit_finish(sess.id, 2, "Juda foydali sessiya", rating=5)
            result = await svc.submit_finish(sess.id, 1, "Yaxshi o'quvchi", rating=4)
            await db.commit()
            assert result.status == SessionStatus.FINISHED.value

        async with maker() as db:
            mentor = await db.get(User, 1)
            mentee = await db.get(User, 2)
            assert mentor.coins == 6  # +1 mukofot
            assert mentor.xp == settings.XP_PER_SESSION  # 0 dan boshlanadi
            assert mentor.total_taught == 1
            assert mentee.xp == settings.XP_PER_SESSION // 2
            assert mentee.total_learned == 1

            slot = await db.get(Slot, slot_id)
            assert slot.status == SlotStatus.FINISHED.value

            # earn_teach tranzaksiyasi aynan bitta (idempotentlik)
            count = (
                await db.execute(
                    select(func.count())
                    .select_from(Transaction)
                    .where(Transaction.type == "earn_teach")
                )
            ).scalar()
            assert count == 1
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_cannot_learn_without_coins():
    """Coin 0 bo'lsa band qilish bloklanadi (Property 1)."""
    engine, maker = await _maker()
    try:
        now = now_local()
        async with maker() as db:
            repo = UserRepository(db)
            await repo.create_or_update(
                user_id=1,
                username=None,
                school21_login="m",
                nickname="m",
            )
            mentee = await repo.create_or_update(
                user_id=2,
                username=None,
                school21_login="me",
                nickname="me",
            )
            mentee.coins = 0
            slot_service = SlotService(db)
            slot = await slot_service.create_slot(
                mentor_id=1,
                direction="python",
                start_time=now + timedelta(hours=1),
                end_time=now + timedelta(hours=2),
            )
            await db.commit()
            slot_id = slot.id

        async with maker() as db:
            slot_service = SlotService(db)
            coin_service = CoinService(db)
            slot = await slot_service.get_slot_by_id(slot_id)
            booked = await slot_service.book_slot(
                slot_id,
                mentee_id=2,
                booking_start=slot.start_time,
                booking_end=slot.start_time + timedelta(hours=1),
            )
            assert booked is True
            deducted = await coin_service.deduct(2, 1, reason="spend_learn")
            assert deducted is False  # coin yetmaydi
            # Kompensatsiya: slotni qaytarish
            await slot_service.repo.release_slot(slot_id)
            await db.commit()

        async with maker() as db:
            slot = await db.get(Slot, slot_id)
            assert slot.status == SlotStatus.OPEN.value
            assert slot.mentee_id is None
    finally:
        await engine.dispose()
