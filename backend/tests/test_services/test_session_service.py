"""SessionService finish oqimi testlari va PBT (Property 5, 8)."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.database import models  # noqa: F401
from bot.database.base import Base
from bot.database.models.enums import SessionStatus, SlotStatus
from bot.database.models.slot import Slot
from bot.database.models.transaction import Transaction
from bot.database.models.user import User
from bot.services.session_service import SessionService


async def _fresh_maker():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def _setup_active_session(db):
    mentor = User(id=10, school21_login="m", coins=5, max_coins=15)
    mentee = User(id=11, school21_login="me", coins=4, max_coins=15)
    db.add_all([mentor, mentee])
    await db.flush()
    now = datetime.utcnow()
    slot = Slot(
        mentor_id=10,
        mentee_id=11,
        direction="python",
        start_time=now,
        end_time=now + timedelta(hours=1),
        status=SlotStatus.ACTIVE.value,
    )
    db.add(slot)
    await db.flush()
    svc = SessionService(db)
    session = await svc.create_session(slot)
    return svc, session


@pytest.mark.asyncio
async def test_finish_requires_both_confirmations(db_session):
    svc, session = await _setup_active_session(db_session)

    # Mentee tasdiqlaydi
    result = await svc.submit_finish(session.id, 11, "Juda foydali sessiya edi", rating=5)
    await db_session.commit()
    assert result.status == SessionStatus.FINISHING.value
    assert result.mentee_confirmed is True
    assert result.mentor_confirmed is False

    mentor = await db_session.get(User, 10)
    assert mentor.coins == 5  # hali mukofot yo'q


@pytest.mark.asyncio
async def test_finish_completes_when_both_confirm(db_session):
    svc, session = await _setup_active_session(db_session)

    await svc.submit_finish(session.id, 11, "Rahmat, juda yaxshi", rating=5)
    result = await svc.submit_finish(session.id, 10, "Yaxshi o'quvchi edi", rating=4)
    await db_session.commit()

    assert result.status == SessionStatus.FINISHED.value
    mentor = await db_session.get(User, 10)
    mentee = await db_session.get(User, 11)
    assert mentor.coins == 6  # +1 mukofot
    assert mentor.xp == 50
    assert mentee.xp == 25
    # mentor reytingi mentee bahosidan (5 -> 100%)
    assert mentor.rating == 100.0
    assert mentee.rating == 80.0  # 4 -> 80%


@pytest.mark.asyncio
async def test_finish_wrong_user_returns_none(db_session):
    svc, session = await _setup_active_session(db_session)
    result = await svc.submit_finish(session.id, 999, "begona", rating=3)
    assert result is None


@given(mentor_first=st.booleans())
@pytest.mark.asyncio
async def test_pbt_reward_once_regardless_of_order(mentor_first):
    """Property 5 & 8: tasdiqlash tartibidan qat'i nazar coin/XP aynan bir marta."""
    engine, maker = await _fresh_maker()
    try:
        async with maker() as db:
            svc, session = await _setup_active_session(db)
            await db.commit()
            sid = session.id

        order = [10, 11] if mentor_first else [11, 10]
        async with maker() as db:
            svc = SessionService(db)
            await svc.submit_finish(sid, order[0], "comment one ok", rating=5)
            await db.commit()
        async with maker() as db:
            svc = SessionService(db)
            res = await svc.submit_finish(sid, order[1], "comment two ok", rating=5)
            await db.commit()
            assert res.status == SessionStatus.FINISHED.value

        # Takroriy finish urinishi (idempotentlikni buzmasligi kerak)
        async with maker() as db:
            svc = SessionService(db)
            await svc.submit_finish(sid, order[0], "again again", rating=1)
            await svc.submit_finish(sid, order[1], "again again2", rating=1)
            await db.commit()

        async with maker() as db:
            mentor = await db.get(User, 10)
            assert mentor.coins == 6  # faqat +1
            assert mentor.xp == 50  # faqat bir marta
            # earn_teach tranzaksiyasi aynan bitta
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
