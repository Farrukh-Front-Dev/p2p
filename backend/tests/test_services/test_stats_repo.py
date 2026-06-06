"""StatsRepository (admin statistika) testlari."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from bot.database.models.enums import SessionStatus, SlotStatus
from bot.database.models.session import Session
from bot.database.models.slot import Slot
from bot.database.models.user import User
from bot.repositories.stats_repo import StatsRepository


@pytest.mark.asyncio
async def test_gather_counts(db_session):
    db_session.add_all(
        [
            User(id=1, school21_login="a", coins=5),
            User(id=2, school21_login="b", coins=10),
        ]
    )
    await db_session.flush()
    now = datetime.utcnow()
    open_slot = Slot(
        mentor_id=1,
        direction="python",
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=2),
        status=SlotStatus.OPEN.value,
    )
    booked_slot = Slot(
        mentor_id=1,
        mentee_id=2,
        direction="sql",
        start_time=now + timedelta(hours=3),
        end_time=now + timedelta(hours=4),
        status=SlotStatus.BOOKED.value,
    )
    db_session.add_all([open_slot, booked_slot])
    await db_session.flush()
    db_session.add(
        Session(
            slot_id=booked_slot.id,
            mentor_id=1,
            mentee_id=2,
            status=SessionStatus.FINISHED.value,
        )
    )
    await db_session.commit()

    stats = await StatsRepository(db_session).gather()
    assert stats["users"] == 2
    assert stats["slots"] == 2
    assert stats["open_slots"] == 1
    assert stats["sessions"] == 1
    assert stats["finished"] == 1
    assert stats["coins"] == 15


@pytest.mark.asyncio
async def test_all_user_ids_excludes_inactive(db_session):
    db_session.add_all(
        [
            User(id=1, school21_login="a", is_active=True),
            User(id=2, school21_login="b", is_active=False),
        ]
    )
    await db_session.commit()

    ids = await StatsRepository(db_session).all_user_ids()
    assert ids == [1]
