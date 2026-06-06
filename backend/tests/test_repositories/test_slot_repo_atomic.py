"""SlotRepository atomik band qilish PBT (Property 3, 4)."""

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
from bot.database.models.enums import SlotStatus
from bot.repositories.slot_repo import SlotRepository
from bot.repositories.user_repo import UserRepository


async def _fresh_sessionmaker():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    return engine, maker


async def _make_users(db, ids: list[int]) -> None:
    repo = UserRepository(db)
    for uid in ids:
        await repo.create_or_update(
            user_id=uid,
            username=None,
            school21_login=f"user{uid}",
            nickname=f"user{uid}",
        )
    await db.flush()


async def _make_open_slot(db, mentor_id: int):
    repo = SlotRepository(db)
    now = datetime.utcnow()
    return await repo.create(
        mentor_id=mentor_id,
        direction="python",
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=2),
        status=SlotStatus.OPEN.value,
    )


@pytest.mark.asyncio
async def test_only_one_mentee_books(db_sessionmaker):
    """Property 3: bir slotni bir nechta mentee band qilishga urinsa, faqat bittasi."""
    async with db_sessionmaker() as db:
        mentor_id = 1
        mentee_ids = [2, 3, 4, 5, 6]
        await _make_users(db, [mentor_id, *mentee_ids])
        slot = await _make_open_slot(db, mentor_id)
        await db.commit()
        slot_id = slot.id

    repo_session = db_sessionmaker
    successes = []
    async with repo_session() as db:
        repo = SlotRepository(db)
        for mentee_id in mentee_ids:
            ok = await repo.book_slot_atomic(slot_id, mentee_id)
            successes.append(ok)
        await db.commit()

    assert successes.count(True) == 1, f"Aynan bitta muvaffaqiyat kutilgan: {successes}"

    async with repo_session() as db:
        repo = SlotRepository(db)
        slot = await repo.get_by_id(slot_id)
        assert slot.status == SlotStatus.BOOKED.value
        assert slot.mentee_id == mentee_ids[0]  # birinchi urinish g'olib


@pytest.mark.asyncio
async def test_mentor_cannot_book_own_slot(db_sessionmaker):
    """Property 4: mentor o'z slotini band qila olmaydi."""
    async with db_sessionmaker() as db:
        await _make_users(db, [10])
        slot = await _make_open_slot(db, mentor_id=10)
        await db.commit()
        slot_id = slot.id

    async with db_sessionmaker() as db:
        repo = SlotRepository(db)
        ok = await repo.book_slot_atomic(slot_id, mentee_id=10)
        await db.commit()
        assert ok is False
        slot = await repo.get_by_id(slot_id)
        assert slot.status == SlotStatus.OPEN.value
        assert slot.mentee_id is None


@given(n_mentees=st.integers(min_value=1, max_value=10))
@pytest.mark.asyncio
async def test_pbt_single_winner(n_mentees):
    """PBT: ixtiyoriy sondagi mentee urinsa ham, aynan bitta g'olib."""
    engine, maker = await _fresh_sessionmaker()
    try:
        mentor_id = 1000
        mentee_ids = list(range(2000, 2000 + n_mentees))

        async with maker() as db:
            await _make_users(db, [mentor_id, *mentee_ids])
            slot = await _make_open_slot(db, mentor_id)
            await db.commit()
            slot_id = slot.id

        success_count = 0
        async with maker() as db:
            repo = SlotRepository(db)
            for mentee_id in mentee_ids:
                if await repo.book_slot_atomic(slot_id, mentee_id):
                    success_count += 1
            await db.commit()

        assert success_count == 1
    finally:
        await engine.dispose()
