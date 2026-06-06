"""ORM modellar testlari."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from bot.database.models import (
    ReviewRole,
    Session,
    SessionStatus,
    Slot,
    SlotStatus,
    Transaction,
    TransactionType,
    User,
)


def test_enum_values():
    assert SlotStatus.OPEN.value == "open"
    assert SlotStatus.BOOKED.value == "booked"
    assert SessionStatus.FINISHED.value == "finished"
    assert TransactionType.EARN_TEACH.value == "earn_teach"
    assert ReviewRole.MENTOR.value == "mentor"


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(id=1, school21_login="toyneden", nickname="Toyne", coins=5)
    db_session.add(user)
    await db_session.commit()

    fetched = await db_session.get(User, 1)
    assert fetched is not None
    assert fetched.school21_login == "toyneden"
    assert fetched.coins == 5
    assert fetched.directions == []  # StringArray default


@pytest.mark.asyncio
async def test_user_directions_array(db_session):
    user = User(
        id=2,
        school21_login="alice",
        directions=["python", "backend", "ml_ai"],
    )
    db_session.add(user)
    await db_session.commit()

    fetched = await db_session.get(User, 2)
    assert fetched.directions == ["python", "backend", "ml_ai"]


@pytest.mark.asyncio
async def test_create_slot_with_uuid(db_session):
    mentor = User(id=10, school21_login="mentor1")
    db_session.add(mentor)
    await db_session.flush()

    now = datetime.utcnow()
    slot = Slot(
        mentor_id=10,
        direction="python",
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=2),
        status=SlotStatus.OPEN.value,
    )
    db_session.add(slot)
    await db_session.commit()

    assert isinstance(slot.id, uuid.UUID)
    fetched = (await db_session.execute(select(Slot))).scalar_one()
    assert fetched.status == "open"
    assert fetched.direction == "python"


@pytest.mark.asyncio
async def test_slot_mentor_relationship(db_session):
    mentor = User(id=20, school21_login="mentor2")
    db_session.add(mentor)
    await db_session.flush()

    now = datetime.utcnow()
    slot = Slot(
        mentor_id=20,
        direction="backend",
        start_time=now,
        end_time=now + timedelta(hours=1),
    )
    db_session.add(slot)
    await db_session.commit()

    await db_session.refresh(slot, ["mentor"])
    assert slot.mentor.school21_login == "mentor2"


@pytest.mark.asyncio
async def test_session_and_transaction(db_session):
    mentor = User(id=30, school21_login="m3")
    mentee = User(id=31, school21_login="me3")
    db_session.add_all([mentor, mentee])
    await db_session.flush()

    now = datetime.utcnow()
    slot = Slot(
        mentor_id=30,
        mentee_id=31,
        direction="sql",
        start_time=now,
        end_time=now + timedelta(hours=1),
        status=SlotStatus.BOOKED.value,
    )
    db_session.add(slot)
    await db_session.flush()

    sess = Session(
        slot_id=slot.id,
        mentor_id=30,
        mentee_id=31,
        status=SessionStatus.ACTIVE.value,
    )
    db_session.add(sess)
    await db_session.flush()

    tx = Transaction(
        user_id=31,
        amount=-1,
        type=TransactionType.SPEND_LEARN.value,
        slot_id=slot.id,
        session_id=sess.id,
    )
    db_session.add(tx)
    await db_session.commit()

    fetched_tx = (await db_session.execute(select(Transaction))).scalar_one()
    assert fetched_tx.amount == -1
    assert fetched_tx.type == "spend_learn"
    assert fetched_tx.session_id == sess.id
