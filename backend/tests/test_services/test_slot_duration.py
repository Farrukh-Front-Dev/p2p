"""Slot yaratish (start+end) va vaqt klaviaturasi testlari."""

from __future__ import annotations

from datetime import datetime, time, timedelta

import pytest

from bot.keyboards.time_picker_kb import (
    get_booking_end_kb,
    get_booking_start_kb,
    get_calendar_kb,
    get_mentor_end_kb,
    get_mentor_start_kb,
)
from bot.repositories.user_repo import UserRepository
from bot.services.slot_service import SlotService, SlotValidationError
from bot.utils.time_utils import now_local


async def _setup(db):
    urepo = UserRepository(db)
    await urepo.create_or_update(1, None, "m", "m")
    mentee = await urepo.create_or_update(2, None, "me", "me")
    mentee.coins = 5
    await db.flush()
    return SlotService(db)


@pytest.mark.asyncio
async def test_create_slot_rejects_past_start(db_session):
    service = await _setup(db_session)
    now = now_local()
    with pytest.raises(SlotValidationError):
        await service.create_slot(
            mentor_id=1,
            direction="python",
            start_time=now - timedelta(minutes=5),
            end_time=now + timedelta(hours=1),
        )


@pytest.mark.asyncio
async def test_create_slot_rejects_end_before_start(db_session):
    service = await _setup(db_session)
    now = now_local()
    start = now + timedelta(hours=2)
    with pytest.raises(SlotValidationError):
        await service.create_slot(
            mentor_id=1,
            direction="python",
            start_time=start,
            end_time=start - timedelta(minutes=30),
        )


@pytest.mark.asyncio
async def test_create_and_book_slot(db_session):
    service = await _setup(db_session)
    now = now_local()
    start = now + timedelta(hours=2)
    end = start + timedelta(hours=3)  # mentor oynasi 3 soat
    slot = await service.create_slot(
        mentor_id=1, direction="python", start_time=start, end_time=end
    )
    await db_session.flush()
    assert slot.start_time == start
    assert slot.end_time == end

    # mentee oyna ichidan 2 soatlik sessiya tanlaydi
    ok = await service.book_slot(
        slot.id,
        mentee_id=2,
        booking_start=start,
        booking_end=start + timedelta(hours=2),
    )
    assert ok is True


@pytest.mark.asyncio
async def test_book_rejects_over_4h(db_session):
    service = await _setup(db_session)
    now = now_local()
    start = now + timedelta(hours=2)
    slot = await service.create_slot(
        mentor_id=1,
        direction="python",
        start_time=start,
        end_time=start + timedelta(hours=8),  # mentor keng oyna ochadi
    )
    await db_session.flush()
    # mentee 5 soat tanlay olmaydi (maks 4)
    with pytest.raises(SlotValidationError):
        await service.book_slot(
            slot.id,
            mentee_id=2,
            booking_start=start,
            booking_end=start + timedelta(hours=5),
        )


@pytest.mark.asyncio
async def test_book_rejects_outside_window(db_session):
    service = await _setup(db_session)
    now = now_local()
    start = now + timedelta(hours=2)
    slot = await service.create_slot(
        mentor_id=1,
        direction="python",
        start_time=start,
        end_time=start + timedelta(hours=2),
    )
    await db_session.flush()
    with pytest.raises(SlotValidationError):
        await service.book_slot(
            slot.id,
            mentee_id=2,
            booking_start=start,
            booking_end=start + timedelta(hours=3),  # oynadan tashqari
        )


@pytest.mark.asyncio
async def test_booking_splits_window(db_session):
    """Oyna o'rtasidan band qilinsa, oldingi va keyingi bo'sh qismlar yangi slot bo'ladi."""
    service = await _setup(db_session)
    now = now_local()
    start = (now + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=5)  # 5 soatlik oyna
    slot = await service.create_slot(
        mentor_id=1, direction="python", start_time=start, end_time=end
    )
    await db_session.flush()

    # O'rtadan 1 soat band qilinadi: [start+1h ... start+2h]
    b_start = start + timedelta(hours=1)
    b_end = start + timedelta(hours=2)
    ok = await service.book_slot(slot.id, mentee_id=2, booking_start=b_start, booking_end=b_end)
    assert ok is True
    await db_session.commit()

    # Mentorning slotlari: 1 booked + 2 open (oldin/keyin)
    all_slots = await service.get_user_slots(1)
    booked = [s for s in all_slots if s.status == "booked"]
    open_slots = sorted((s for s in all_slots if s.status == "open"), key=lambda s: s.start_time)
    assert len(booked) == 1
    assert booked[0].start_time == b_start
    assert booked[0].end_time == b_end
    assert len(open_slots) == 2
    # Oldingi qism: start → b_start
    assert open_slots[0].start_time == start
    assert open_slots[0].end_time == b_start
    # Keyingi qism: b_end → end
    assert open_slots[1].start_time == b_end
    assert open_slots[1].end_time == end


@pytest.mark.asyncio
async def test_booking_from_start_leaves_one_leftover(db_session):
    """Oyna boshidan band qilinsa, faqat keyingi qism bo'sh qoladi."""
    service = await _setup(db_session)
    now = now_local()
    start = (now + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=3)
    slot = await service.create_slot(
        mentor_id=1, direction="python", start_time=start, end_time=end
    )
    await db_session.flush()

    b_end = start + timedelta(hours=1)
    await service.book_slot(slot.id, mentee_id=2, booking_start=start, booking_end=b_end)
    await db_session.commit()

    all_slots = await service.get_user_slots(1)
    open_slots = [s for s in all_slots if s.status == "open"]
    assert len(open_slots) == 1
    assert open_slots[0].start_time == b_end
    assert open_slots[0].end_time == end


# ---- Klaviatura testlari ----


def test_calendar_kb_has_nav_and_days():
    now = datetime(2026, 6, 15, 10, 0)
    kb = get_calendar_kb(2026, 6, now=now)
    nav = kb.inline_keyboard[0]
    assert len(nav) == 3
    assert "Iyun 2026" in nav[1].text
    day_btns = [
        b
        for row in kb.inline_keyboard
        for b in row
        if b.callback_data and b.callback_data.startswith("calday_")
    ]
    assert len(day_btns) > 0


def test_calendar_past_days_blocked():
    now = datetime(2026, 6, 15, 10, 0)
    kb = get_calendar_kb(2026, 6, now=now)
    day_isos = [
        b.callback_data.replace("calday_", "")
        for row in kb.inline_keyboard
        for b in row
        if b.callback_data and b.callback_data.startswith("calday_")
    ]
    assert "2026-06-15" in day_isos
    assert "2026-06-14" not in day_isos


def test_mentor_start_today_only_future():
    now = datetime(2026, 6, 5, 14, 17)
    kb = get_mentor_start_kb(now.date(), now=now)
    times = [
        datetime.fromisoformat(b.callback_data.replace("mstart_", ""))
        for row in kb.inline_keyboard
        for b in row
        if b.callback_data and b.callback_data.startswith("mstart_")
    ]
    assert all(t > now for t in times)
    assert times[0].hour == 14 and times[0].minute == 30


def test_mentor_end_goes_to_midnight_no_cap():
    """Mentor uchun tugash vaqti cheklovi YO'Q — 24:00 gacha."""
    start = datetime(2026, 6, 6, 10, 0)
    kb = get_mentor_end_kb(start)
    ends = [
        datetime.fromisoformat(b.callback_data.replace("mend_", ""))
        for row in kb.inline_keyboard
        for b in row
        if b.callback_data and b.callback_data.startswith("mend_")
    ]
    midnight = datetime.combine(start.date(), time(0, 0)) + timedelta(days=1)
    assert min(ends) == start + timedelta(minutes=30)
    assert max(ends) == midnight  # 4 soat bilan cheklanmagan


def test_booking_end_caps_at_4h():
    """Mentee uchun tugash vaqti maksimal 4 soat bilan cheklangan."""
    start = datetime(2026, 6, 6, 10, 0)
    window_end = datetime(2026, 6, 6, 20, 0)  # 10 soatlik oyna
    kb = get_booking_end_kb(start, window_end)
    ends = [
        datetime.fromisoformat(b.callback_data.replace("bend_", ""))
        for row in kb.inline_keyboard
        for b in row
        if b.callback_data and b.callback_data.startswith("bend_")
    ]
    assert max(ends) == start + timedelta(hours=4)  # 4 soat cap


def test_booking_end_respects_window():
    start = datetime(2026, 6, 6, 10, 0)
    window_end = datetime(2026, 6, 6, 11, 30)  # atigi 1.5 soat
    kb = get_booking_end_kb(start, window_end)
    ends = [
        datetime.fromisoformat(b.callback_data.replace("bend_", ""))
        for row in kb.inline_keyboard
        for b in row
        if b.callback_data and b.callback_data.startswith("bend_")
    ]
    assert max(ends) == window_end


def test_booking_start_within_window():
    window_start = datetime(2026, 6, 6, 10, 0)
    window_end = datetime(2026, 6, 6, 12, 0)
    kb = get_booking_start_kb(window_start, window_end)
    starts = [
        datetime.fromisoformat(b.callback_data.replace("bstart_", ""))
        for row in kb.inline_keyboard
        for b in row
        if b.callback_data and b.callback_data.startswith("bstart_")
    ]
    assert min(starts) == window_start
    assert all(window_start <= s < window_end for s in starts)


@pytest.mark.asyncio
async def test_update_open_slot_changes_direction(db_session):
    service = await _setup(db_session)
    now = now_local()
    start = now + timedelta(hours=2)
    slot = await service.create_slot(
        mentor_id=1, direction="python", start_time=start, end_time=start + timedelta(hours=2)
    )
    await db_session.flush()

    updated = await service.update_slot(slot.id, mentor_id=1, direction="backend")
    assert updated is not None
    assert updated.direction == "backend"


@pytest.mark.asyncio
async def test_update_open_slot_changes_time(db_session):
    service = await _setup(db_session)
    now = now_local()
    start = now + timedelta(hours=2)
    slot = await service.create_slot(
        mentor_id=1, direction="python", start_time=start, end_time=start + timedelta(hours=2)
    )
    await db_session.flush()

    new_start = now + timedelta(hours=5)
    new_end = new_start + timedelta(hours=1)
    updated = await service.update_slot(
        slot.id, mentor_id=1, start_time=new_start, end_time=new_end
    )
    assert updated.start_time == new_start
    assert updated.end_time == new_end


@pytest.mark.asyncio
async def test_cannot_edit_booked_slot(db_session):
    service = await _setup(db_session)
    now = now_local()
    start = now + timedelta(hours=2)
    slot = await service.create_slot(
        mentor_id=1, direction="python", start_time=start, end_time=start + timedelta(hours=2)
    )
    await db_session.flush()
    await service.book_slot(
        slot.id, mentee_id=2, booking_start=start, booking_end=start + timedelta(hours=1)
    )

    # Band qilingan (booked) slotni tahrirlab bo'lmaydi
    result = await service.update_slot(slot.id, mentor_id=1, direction="backend")
    assert result is None


@pytest.mark.asyncio
async def test_cannot_edit_others_slot(db_session):
    service = await _setup(db_session)
    now = now_local()
    start = now + timedelta(hours=2)
    slot = await service.create_slot(
        mentor_id=1, direction="python", start_time=start, end_time=start + timedelta(hours=2)
    )
    await db_session.flush()
    result = await service.update_slot(slot.id, mentor_id=999, direction="backend")
    assert result is None
