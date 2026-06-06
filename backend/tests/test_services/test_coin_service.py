"""CoinService testlari va PBT (Property 1, 2, 5, 9)."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import select
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
from bot.database.models.transaction import Transaction
from bot.database.models.user import User
from bot.services.coin_service import CoinService


async def _fresh_maker():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.mark.asyncio
async def test_deduct_success(db_session):
    db_session.add(User(id=1, school21_login="u1", coins=5, max_coins=15))
    await db_session.flush()

    svc = CoinService(db_session)
    ok = await svc.deduct(1, 1, reason="spend_learn")
    await db_session.commit()

    assert ok is True
    user = await db_session.get(User, 1)
    assert user.coins == 4
    txs = (await db_session.execute(select(Transaction))).scalars().all()
    assert len(txs) == 1
    assert txs[0].amount == -1


@pytest.mark.asyncio
async def test_deduct_insufficient_balance(db_session):
    db_session.add(User(id=2, school21_login="u2", coins=0, max_coins=15))
    await db_session.flush()

    svc = CoinService(db_session)
    ok = await svc.deduct(2, 1)
    await db_session.commit()

    assert ok is False
    user = await db_session.get(User, 2)
    assert user.coins == 0
    txs = (await db_session.execute(select(Transaction))).scalars().all()
    assert len(txs) == 0  # muvaffaqiyatsiz deduct tranzaksiya yozmaydi


async def _make_session_with_users(db, mentor_coins=5, max_coins=15):
    mentor = User(id=10, school21_login="m", coins=mentor_coins, max_coins=max_coins)
    mentee = User(id=11, school21_login="me", coins=5, max_coins=max_coins)
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
    sess = Session(
        slot_id=slot.id,
        mentor_id=10,
        mentee_id=11,
        status=SessionStatus.ACTIVE.value,
    )
    db.add(sess)
    await db.flush()
    return sess


@pytest.mark.asyncio
async def test_reward_mentor_idempotent(db_session):
    sess = await _make_session_with_users(db_session, mentor_coins=5)
    svc = CoinService(db_session)

    first = await svc.reward_mentor(sess)
    second = await svc.reward_mentor(sess)
    await db_session.commit()

    assert first is True
    assert second is False  # Property 5: ikkinchi marta bermaydi
    mentor = await db_session.get(User, 10)
    assert mentor.coins == 6  # faqat bir marta +1


@pytest.mark.asyncio
async def test_reward_mentor_respects_cap(db_session):
    sess = await _make_session_with_users(db_session, mentor_coins=15, max_coins=15)
    svc = CoinService(db_session)

    await svc.reward_mentor(sess)
    await db_session.commit()

    mentor = await db_session.get(User, 10)
    assert mentor.coins == 15  # Property 2: cap dan oshmaydi
    # cap'da hech narsa qo'shilmagani uchun tranzaksiya yozilmaydi
    txs = (await db_session.execute(select(Transaction))).scalars().all()
    assert len(txs) == 0


@given(
    start_coins=st.integers(min_value=0, max_value=15),
    deduct_seq=st.lists(st.integers(min_value=1, max_value=3), max_size=12),
)
@pytest.mark.asyncio
async def test_pbt_coins_never_negative(start_coins, deduct_seq):
    """Property 1: ketma-ket deduct'lardan keyin ham coins >= 0."""
    engine, maker = await _fresh_maker()
    try:
        async with maker() as db:
            db.add(User(id=1, school21_login="u", coins=start_coins, max_coins=15))
            await db.flush()
            svc = CoinService(db)
            for amount in deduct_seq:
                await svc.deduct(1, amount)
            await db.commit()

        async with maker() as db:
            user = await db.get(User, 1)
            assert user.coins >= 0
            # Property 9: har muvaffaqiyatli deduct uchun tranzaksiya bor
            txs = (await db.execute(select(Transaction))).scalars().all()
            total_deducted = start_coins - user.coins
            assert sum(-t.amount for t in txs) == total_deducted
    finally:
        await engine.dispose()
