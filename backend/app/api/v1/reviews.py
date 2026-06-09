"""Review endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.db.models.review import Review
from app.db.models.slot import Slot, SlotStatus
from app.schemas.review import ReviewCreate, ReviewOut
from app.services.notification_service import create_notification

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(payload: ReviewCreate, user: CurrentUser, db: DbSession):
    slot = await db.get(Slot, payload.slot_id)
    if slot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found"
        )
    if slot.status != SlotStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviews allowed only after slot completion",
        )
    if user.id == slot.reviewer_id:
        target_id = slot.reviewee_id
    elif user.id == slot.reviewee_id:
        target_id = slot.reviewer_id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a slot participant"
        )

    existing = (
        await db.execute(
            select(Review).where(
                Review.slot_id == slot.id, Review.author_id == user.id
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already reviewed this slot",
        )

    review = Review(
        slot_id=slot.id,
        author_id=user.id,
        target_id=target_id,
        is_positive=payload.is_positive,
        comment=payload.comment,
    )
    db.add(review)
    await create_notification(
        db, target_id, "review_received", "Yangi sharh", slot_id=slot.id
    )
    await db.commit()
    await db.refresh(review)
    return review


@router.get("/my", response_model=list[ReviewOut])
async def my_reviews(user: CurrentUser, db: DbSession):
    stmt = select(Review).where(Review.target_id == user.id)
    return (await db.execute(stmt)).scalars().all()


@router.get("/user/{user_id}", response_model=list[ReviewOut])
async def user_reviews(user_id: uuid.UUID, user: CurrentUser, db: DbSession):
    stmt = select(Review).where(Review.target_id == user_id)
    return (await db.execute(stmt)).scalars().all()
