"""XPService va level_utils testlari/PBT (Property 5, 10)."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.database import models  # noqa: F401
from bot.database.base import Base
from bot.database.models.enums import SessionStatus, SlotStatus
from bot.database.models.session import Session
from bot.database.models.slot import Slot
from bot.database.models.user import User
from bot.services.xp_service import XPService
from bot.utils.level_utils import XP_TABLE, calculate_level, get_level_info


def test_calculate_level_boundaries():
    assert calculate_level(0) == 1
    assert calculate_level(99) == 1
    assert calculate_level(100) == 2
    assert calculate_level(249) == 2
    assert calculate_level(250) == 3
    assert calculate_level(999) == 4
    assert calculate_level(1000) == 5
    assert calculate_level(4999) == 6
    assert calculate_level(5000) == 7
    assert calculate_level(999999) == 7


def test_get_level_info_progress():
    info = get_level_info(0)
    assert info["level"] == 1
    assert info["next_level_xp"] == 100
    assert info["progress"] == 0

    info = get_level_info(50)
    assert info["level"] == 1
    assert info["progress"] == 50

    info_max = get_level_info(6000)
    assert info_max["level"] == 7
    assert info_max["progress"] == 100
    assert info_max["next_level_xp"] is None


@given(xp=st.integers(min_value=0, max_value=200000))
def test_pbt_level_monotonic_and_consistent(xp):
    """Property 10: level XP jadvaliga mos va monoton."""
    level = calculate_level(xp)
    # Level chegarasiga mos
    assert xp >= XP_TABLE[level]
    if level < max(XP_TABLE):
        assert xp < XP_TABLE[level + 1]
    # Monotonlik: XP ortsa level kamaymaydi
    assert calculate_level(xp) <= calculate_level(xp + 1)


async def _fresh_maker():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def _make_session(db, mentor_xp=0, mentee_xp=0):
    mentor = User(id=10, school21_login="m", xp=mentor_xp, level=calculate_level(mentor_xp))
    mentee = User(id=11, school21_login="me", xp=mentee_xp, level=calculate_level(mentee_xp))
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
    sess = Session(slot_id=slot.id, mentor_id=10, mentee_id=11, status=SessionStatus.ACTIVE.value)
    db.add(sess)
    await db.flush()
    return sess


@pytest.mark.asyncio
async def test_award_xp_basic(db_session):
    sess = await _make_session(db_session)
    svc = XPService(db_session)
    result = await svc.award_xp(sess)
    await db_session.commit()

    assert result["mentor_xp_gained"] == 50
    assert result["mentee_xp_gained"] == 25
    mentor = await db_session.get(User, 10)
    mentee = await db_session.get(User, 11)
    assert mentor.xp == 50
    assert mentor.total_taught == 1
    assert mentee.xp == 25
    assert mentee.total_learned == 1


@pytest.mark.asyncio
async def test_award_xp_idempotent(db_session):
    sess = await _make_session(db_session)
    svc = XPService(db_session)
    await svc.award_xp(sess)
    second = await svc.award_xp(sess)
    await db_session.commit()

    assert second is None  # Property 5
    mentor = await db_session.get(User, 10)
    assert mentor.xp == 50  # ikki marta qo'shilmagan
    assert mentor.total_taught == 1


@pytest.mark.asyncio
async def test_award_xp_level_up(db_session):
    # mentor 60 XP -> +50 = 110 -> level 2
    sess = await _make_session(db_session, mentor_xp=60)
    svc = XPService(db_session)
    result = await svc.award_xp(sess)
    await db_session.commit()

    assert result["mentor_leveled_up"] is True
    assert result["mentor_level"] == 2


@given(
    mentor_xp=st.integers(min_value=0, max_value=10000),
    mentee_xp=st.integers(min_value=0, max_value=10000),
)
@pytest.mark.asyncio
async def test_pbt_award_keeps_level_consistent(mentor_xp, mentee_xp):
    """Property 10: award_xp'dan keyin level har doim xp'ga mos."""
    engine, maker = await _fresh_maker()
    try:
        async with maker() as db:
            sess = await _make_session(db, mentor_xp=mentor_xp, mentee_xp=mentee_xp)
            svc = XPService(db)
            await svc.award_xp(sess)
            await db.commit()

        async with maker() as db:
            mentor = await db.get(User, 10)
            mentee = await db.get(User, 11)
            assert mentor.level == calculate_level(mentor.xp)
            assert mentee.level == calculate_level(mentee.xp)
    finally:
        await engine.dispose()
