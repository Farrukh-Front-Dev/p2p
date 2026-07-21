"""Slot-related background tasks: reminders, reveal, absence checks."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db.base import AsyncSessionLocal
from app.db.models.slot import Slot, SlotStatus
from app.services.notification_service import create_notification
from app.tasks.async_utils import run_async
from app.tasks.celery_app import celery_app

REMINDER_LEAD_MINUTES = 15
ABSENT_GRACE_MINUTES = 15


@celery_app.task(name="app.tasks.slot_tasks.send_slot_reminders")
def send_slot_reminders() -> int:
    return run_async(_send_slot_reminders())


async def _send_slot_reminders() -> int:
    """Notify both parties 15 min before start. Only booked slots qualify."""
    now = datetime.now(timezone.utc)
    window_start = now + timedelta(minutes=REMINDER_LEAD_MINUTES)
    window_end = window_start + timedelta(minutes=1)
    sent = 0
    async with AsyncSessionLocal() as db:
        stmt = select(Slot).where(
            Slot.status == SlotStatus.BOOKED.value,
            Slot.start_time >= window_start,
            Slot.start_time < window_end,
        )
        slots = (await db.execute(stmt)).scalars().all()
        for slot in slots:
            await create_notification(
                db, slot.reviewer_id, "slot_reminder",
                "Slot yaqinda boshlanadi", slot_id=slot.id,
            )
            # Reveal the reviewee identity to the reviewer.
            await create_notification(
                db, slot.reviewer_id, "slot_revealed",
                "O'rganuvchi ma'lumoti", slot_id=slot.id,
            )
            if slot.reviewee_id:
                await create_notification(
                    db, slot.reviewee_id, "slot_reminder",
                    "Slot yaqinda boshlanadi", slot_id=slot.id,
                )
            sent += 1
        await db.commit()
    return sent


@celery_app.task(name="app.tasks.slot_tasks.check_absences")
def check_absences() -> int:
    return run_async(_check_absences())


async def _check_absences() -> int:
    """Placeholder hook: absences are user-driven, this surfaces stale slots."""
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(minutes=ABSENT_GRACE_MINUTES)
    async with AsyncSessionLocal() as db:
        stmt = select(Slot).where(
            Slot.status == SlotStatus.BOOKED.value,
            Slot.start_time < threshold,
        )
        slots = (await db.execute(stmt)).scalars().all()
        return len(slots)
