"""get_user_slots va get_leaderboard testlari."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from bot.database.models.enums import SlotStatus
from bot.repositories.slot_repo import SlotRepository
from bot.repositories.user_repo import UserRepository


@pytest.mark.asyncio
async def test_get_user_slots_returns_mentor_and_mentee(db_session):
    urepo = UserRepository(db_session)
    await urepo.create_or_update(1, None, "m", "m")
    await urepo.create_or_update(2, None, "me", "me")
    await db_session.flush()

    srepo = SlotRepository(db_session)
    now = datetime.utcnow()
    # 1 mentor sifatida
    await srepo.create(
        mentor_id=1,
        direction="python",
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=2),
        status=SlotStatus.OPEN.value,
    )
    # 2 mentee sifatida (1 mentor)
    await srepo.create(
        mentor_id=1,
        mentee_id=2,
        direction="sql",
        start_time=now + timedelta(hours=3),
        end_time=now + timedelta(hours=4),
        status=SlotStatus.BOOKED.value,
    )
    await db_session.commit()

    mentor_slots = await srepo.get_user_slots(1)
    mentee_slots = await srepo.get_user_slots(2)
    assert len(mentor_slots) == 2  # 1 ikkalasida ham mentor
    assert len(mentee_slots) == 1


@pytest.mark.asyncio
async def test_get_leaderboard_orders_by_xp(db_session):
    urepo = UserRepository(db_session)
    await urepo.create_or_update(1, None, "a", "a")
    await urepo.create_or_update(2, None, "b", "b")
    await urepo.create_or_update(3, None, "c", "c")
    await urepo.update(1, xp=500, level=4, total_taught=3)
    await urepo.update(2, xp=1200, level=5, total_taught=8)
    await urepo.update(3, xp=100, level=2, total_taught=1)
    await db_session.commit()

    top = await urepo.get_leaderboard(limit=10)
    assert [u.id for u in top] == [2, 1, 3]  # XP kamayish tartibida


@pytest.mark.asyncio
async def test_get_leaderboard_excludes_inactive(db_session):
    urepo = UserRepository(db_session)
    await urepo.create_or_update(1, None, "a", "a")
    await urepo.update(1, xp=999, is_active=False)
    await db_session.commit()

    top = await urepo.get_leaderboard()
    assert top == []
