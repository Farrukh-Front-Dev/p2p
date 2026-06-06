"""Slot bekor qilish (cancel + refund) testlari."""

from __future__ import annotations

from datetime import timedelta

import pytest
from sqlalchemy import func, select

from bot.database.models.enums import SlotStatus
from bot.database.models.transaction import Transaction
from bot.database.models.user import User
from bot.repositories.user_repo import UserRepository
from bot.services.coin_service import CoinService
from bot.services.slot_service import SlotService
from bot.utils.time_utils import now_local


async def _setup(db, mentee_coins=4):
    urepo = UserRepository(db)
    await urepo.create_or_update(1, None, "m", "m")
    mentee = await urepo.create_or_update(2, None, "me", "me")
    mentee.coins = mentee_coins
    await db.flush()
    return SlotService(db)


async def _make_slot(service, hours_from_now=1):
    now = now_local()
    start = now + timedelta(hours=hours_from_now)
    return await service.create_slot(
        mentor_id=1,
        direction="python",
        start_time=start,
        end_time=start + timedelta(hours=1),
    )


@pytest.mark.asyncio
async def test_cancel_open_slot_no_refund(db_session):
    service = await _setup(db_session)
    slot = await _make_slot(service)
    await db_session.commit()

    result = await service.cancel_slot(slot.id, mentor_id=1)
    await db_session.commit()

    assert result is not None
    assert result["refunded_mentee_id"] is None
    refreshed = await service.get_slot_by_id(slot.id)
    assert refreshed.status == SlotStatus.CANCELLED.value


@pytest.mark.asyncio
async def test_cancel_booked_slot_refunds_mentee(db_session):
    service = await _setup(db_session, mentee_coins=4)
    slot = await _make_slot(service)
    await db_session.flush()
    # mentee band qiladi + coin sarflaydi
    await service.book_slot(
        slot.id,
        mentee_id=2,
        booking_start=slot.start_time,
        booking_end=slot.end_time,
    )
    await CoinService(db_session).deduct(2, 1, reason="spend_learn", slot_id=slot.id)
    await db_session.commit()

    mentee = await db_session.get(User, 2)
    assert mentee.coins == 3

    result = await service.cancel_slot(slot.id, mentor_id=1)
    await db_session.commit()

    assert result["refunded_mentee_id"] == 2
    mentee = await db_session.get(User, 2)
    assert mentee.coins == 4  # tanga qaytarildi
    count = (
        await db_session.execute(
            select(func.count()).select_from(Transaction).where(Transaction.amount == 1)
        )
    ).scalar()
    assert count == 1


@pytest.mark.asyncio
async def test_cannot_cancel_others_slot(db_session):
    service = await _setup(db_session)
    slot = await _make_slot(service)
    await db_session.commit()

    result = await service.cancel_slot(slot.id, mentor_id=999)
    assert result is None
    refreshed = await service.get_slot_by_id(slot.id)
    assert refreshed.status == SlotStatus.OPEN.value


@pytest.mark.asyncio
async def test_cannot_cancel_finished_slot(db_session):
    service = await _setup(db_session)
    slot = await _make_slot(service)
    await service.repo.update_status(slot.id, SlotStatus.FINISHED)
    await db_session.commit()

    result = await service.cancel_slot(slot.id, mentor_id=1)
    assert result is None
