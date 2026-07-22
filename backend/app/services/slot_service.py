"""Slot lifecycle business logic: create, book, start, finish, absent, cancel."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.slot import Slot, SlotStatus
from app.db.models.user import User
from app.services import points_service, xp_service
from app.services.notification_service import create_notification

XP_REWARD_COMPLETE = 25
XP_PENALTY_ABSENT = 15
FINISH_MIN_MINUTES = 15
ABSENT_GRACE_MINUTES = 15


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def create_slot(
    db: AsyncSession,
    reviewer: User,
    *,
    reviewer_project: str,
    start_time: datetime,
    end_time: datetime,
    campus: str,
    is_online: bool,
) -> Slot:
    # Tashkent → online only.
    if campus == "tashkent" and not is_online:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tashkent campus slots must be online",
        )
    slot = Slot(
        reviewer_id=reviewer.id,
        reviewer_project=reviewer_project,
        start_time=start_time,
        end_time=end_time,
        campus=campus,
        is_online=is_online,
        status=SlotStatus.OPEN.value,
    )
    db.add(slot)
    await db.flush()
    return slot


async def book_slot(
    db: AsyncSession, slot: Slot, reviewee: User, reviewee_project: str | None
) -> Slot:
    if slot.status != SlotStatus.OPEN.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Slot is not open"
        )
    if slot.reviewer_id == reviewee.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book your own slot",
        )
    if not points_service.can_book_slot(reviewee):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough peer points",
        )

    slot.reviewee_id = reviewee.id
    slot.reviewee_project = reviewee_project
    slot.status = SlotStatus.BOOKED.value
    points_service.add_peer_points(reviewee, -1)

    await create_notification(
        db, slot.reviewer_id, "slot_booked", "Slot band qilindi", slot_id=slot.id
    )
    await create_notification(
        db, reviewee.id, "slot_booked", "Slot band qilindi", slot_id=slot.id
    )
    await db.flush()
    return slot


async def start_slot(db: AsyncSession, slot: Slot, user: User) -> Slot:
    if slot.status not in (SlotStatus.BOOKED.value, SlotStatus.IN_PROGRESS.value):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot cannot be started in its current state",
        )
    if user.id == slot.reviewer_id:
        slot.reviewer_started = True
    elif user.id == slot.reviewee_id:
        slot.reviewee_started = True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a slot participant"
        )

    if slot.reviewer_started and slot.reviewee_started and slot.actual_start is None:
        slot.actual_start = _now()
        slot.status = SlotStatus.IN_PROGRESS.value
    await db.flush()
    return slot


async def finish_slot(db: AsyncSession, slot: Slot, user: User) -> Slot:
    if slot.status != SlotStatus.IN_PROGRESS.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Slot is not in progress"
        )
    if slot.actual_start is not None:
        elapsed = (_now() - slot.actual_start).total_seconds() / 60
        if elapsed < FINISH_MIN_MINUTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Finish becomes available 15 minutes after start",
            )

    if user.id == slot.reviewer_id:
        slot.reviewer_finished = True
    elif user.id == slot.reviewee_id:
        slot.reviewee_finished = True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a slot participant"
        )

    if slot.reviewer_finished and slot.reviewee_finished:
        slot.actual_end = _now()
        if slot.actual_start:
            slot.duration_minutes = int(
                (slot.actual_end - slot.actual_start).total_seconds() / 60
            )
        slot.status = SlotStatus.COMPLETED.value
        reviewer = await db.get(User, slot.reviewer_id)
        if reviewer:
            await xp_service.apply_xp(
                db, reviewer, XP_REWARD_COMPLETE, "slot_completed", slot.id
            )
    await db.flush()
    return slot


async def mark_absent(db: AsyncSession, slot: Slot, actor: User) -> Slot:
    """Mark the other party as absent. Applies XP/point rules per spec 9.6."""
    if slot.status not in (SlotStatus.BOOKED.value, SlotStatus.IN_PROGRESS.value):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Absent can only be marked on booked/in-progress slots",
        )

    reviewer = await db.get(User, slot.reviewer_id)
    reviewee = await db.get(User, slot.reviewee_id) if slot.reviewee_id else None
    if reviewer is None or reviewee is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Slot has no reviewee"
        )

    if actor.id == slot.reviewee_id:
        # Reviewee marks reviewer absent.
        await xp_service.apply_xp(
            db, reviewer, -XP_PENALTY_ABSENT, "absent_received", slot.id
        )
        points_service.add_peer_points(reviewee, 1)  # refund booking
        absent_target = reviewer
    elif actor.id == slot.reviewer_id:
        # Reviewer marks reviewee absent.
        await xp_service.apply_xp(
            db, reviewee, -XP_PENALTY_ABSENT, "absent_received", slot.id
        )
        points_service.add_peer_points(reviewee, -1)  # extra penalty
        absent_target = reviewee
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a slot participant"
        )

    slot.status = SlotStatus.ABSENT.value
    slot.absent_by = actor.id
    slot.absent_at = _now()

    await create_notification(
        db, absent_target.id, "absent_given", "Absens oldingiz", slot_id=slot.id
    )
    await db.flush()
    return slot


async def cancel_slot(
    db: AsyncSession, slot: Slot, actor: User, reason: str | None = None
) -> Slot:
    if slot.status in (
        SlotStatus.COMPLETED.value,
        SlotStatus.CANCELLED.value,
        SlotStatus.ABSENT.value,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot cannot be cancelled in its current state",
        )
    if actor.id != slot.reviewer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the reviewer can cancel the slot",
        )

    # Refund the reviewee's booking point if it was booked.
    if slot.status == SlotStatus.BOOKED.value and slot.reviewee_id:
        reviewee = await db.get(User, slot.reviewee_id)
        if reviewee:
            points_service.add_peer_points(reviewee, 1)
            await create_notification(
                db, reviewee.id, "slot_cancelled", "Slot bekor qilindi", slot_id=slot.id
            )

    slot.status = SlotStatus.CANCELLED.value
    slot.cancelled_by = actor.id
    slot.cancel_reason = reason
    await db.flush()
    return slot
