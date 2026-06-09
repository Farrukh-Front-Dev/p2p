"""Admin REST endpoints (separate from SQLAdmin UI). Requires is_admin."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select

from app.core.dependencies import CurrentAdmin, DbSession
from app.db.models.review import Review
from app.db.models.slot import Slot, SlotStatus
from app.db.models.user import User
from app.schemas.slot import SlotOut
from app.schemas.user import UserMe
from app.services import points_service, xp_service
from app.services.notification_service import create_notification

router = APIRouter(prefix="/admin", tags=["admin"])


class AdjustXp(BaseModel):
    user_id: uuid.UUID
    amount: int


class AdjustPoints(BaseModel):
    user_id: uuid.UUID
    points: int = 0
    coins: int = 0


class NotifyRequest(BaseModel):
    user_id: uuid.UUID | None = None  # None => broadcast
    title: str
    body: str


async def _get_user_or_404(db: DbSession, user_id: uuid.UUID) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/users", response_model=list[UserMe])
async def list_users(
    admin: CurrentAdmin,
    db: DbSession,
    q: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(User)
    if q:
        stmt = stmt.where(User.school21_login.ilike(f"%{q}%"))
    stmt = stmt.limit(limit).offset(offset)
    return (await db.execute(stmt)).scalars().all()


@router.get("/users/{user_id}", response_model=UserMe)
async def get_user(user_id: uuid.UUID, admin: CurrentAdmin, db: DbSession):
    return await _get_user_or_404(db, user_id)


@router.post("/users/{user_id}/block", response_model=UserMe)
async def block_user(user_id: uuid.UUID, admin: CurrentAdmin, db: DbSession):
    user = await _get_user_or_404(db, user_id)
    user.is_active = not user.is_active
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, admin: CurrentAdmin, db: DbSession):
    user = await _get_user_or_404(db, user_id)
    await db.delete(user)
    await db.commit()
    return None


@router.get("/slots", response_model=list[SlotOut])
async def list_slots(
    admin: CurrentAdmin,
    db: DbSession,
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(Slot)
    if status_filter:
        stmt = stmt.where(Slot.status == status_filter)
    stmt = stmt.order_by(Slot.start_time.desc()).limit(limit).offset(offset)
    return (await db.execute(stmt)).scalars().all()


@router.post("/slots/{slot_id}/resolve", response_model=SlotOut)
async def resolve_slot(slot_id: uuid.UUID, admin: CurrentAdmin, db: DbSession):
    """Resolve a dispute: refund booking point to the reviewee."""
    slot = await db.get(Slot, slot_id)
    if slot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found"
        )
    if slot.reviewee_id:
        reviewee = await db.get(User, slot.reviewee_id)
        if reviewee:
            points_service.add_peer_points(reviewee, 1)
    slot.status = SlotStatus.CANCELLED.value
    await db.commit()
    await db.refresh(slot)
    return slot


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: uuid.UUID, admin: CurrentAdmin, db: DbSession):
    review = await db.get(Review, review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    await db.delete(review)
    await db.commit()
    return None


@router.post("/adjust-xp", response_model=UserMe)
async def adjust_xp(payload: AdjustXp, admin: CurrentAdmin, db: DbSession):
    user = await _get_user_or_404(db, payload.user_id)
    await xp_service.apply_xp(db, user, payload.amount, "admin_adjust")
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/adjust-points", response_model=UserMe)
async def adjust_points(payload: AdjustPoints, admin: CurrentAdmin, db: DbSession):
    user = await _get_user_or_404(db, payload.user_id)
    if payload.points:
        points_service.add_peer_points(user, payload.points)
    if payload.coins:
        points_service.add_peer_coins(user, payload.coins)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/notify", status_code=status.HTTP_202_ACCEPTED)
async def notify(payload: NotifyRequest, admin: CurrentAdmin, db: DbSession):
    if payload.user_id:
        await create_notification(
            db, payload.user_id, "system", payload.title, payload.body
        )
    else:
        users = (await db.execute(select(User.id))).scalars().all()
        for uid in users:
            await create_notification(db, uid, "system", payload.title, payload.body)
    await db.commit()
    return {"status": "queued"}


@router.get("/stats")
async def stats(admin: CurrentAdmin, db: DbSession):
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_slots = (await db.execute(select(func.count(Slot.id)))).scalar_one()
    completed = (
        await db.execute(
            select(func.count(Slot.id)).where(
                Slot.status == SlotStatus.COMPLETED.value
            )
        )
    ).scalar_one()
    avg_duration = (
        await db.execute(
            select(func.avg(Slot.duration_minutes)).where(
                Slot.duration_minutes.isnot(None)
            )
        )
    ).scalar_one()
    return {
        "total_users": total_users,
        "total_slots": total_slots,
        "completed_slots": completed,
        "avg_duration_minutes": float(avg_duration) if avg_duration else 0.0,
    }
