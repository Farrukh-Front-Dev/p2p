"""Profile endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.core.dependencies import CurrentUser, DbSession
from app.core.security import decrypt_token
from app.db.models.review import Review
from app.db.models.slot import Slot, SlotStatus
from app.db.models.user import User
from app.schemas.user import ProfileUpdate, UserMe, UserPublic
from app.services.school21_client import school21_client

router = APIRouter(prefix="/profile", tags=["profile"])


async def _review_stats(db: DbSession, user_id: uuid.UUID) -> dict:
    positive = (
        await db.execute(
            select(func.count(Review.id)).where(
                Review.target_id == user_id, Review.is_positive.is_(True)
            )
        )
    ).scalar_one()
    negative = (
        await db.execute(
            select(func.count(Review.id)).where(
                Review.target_id == user_id, Review.is_positive.is_(False)
            )
        )
    ).scalar_one()
    taught = (
        await db.execute(
            select(func.count(Slot.id)).where(
                Slot.reviewer_id == user_id,
                Slot.status == SlotStatus.COMPLETED.value,
            )
        )
    ).scalar_one()
    learned = (
        await db.execute(
            select(func.count(Slot.id)).where(
                Slot.reviewee_id == user_id,
                Slot.status == SlotStatus.COMPLETED.value,
            )
        )
    ).scalar_one()
    return {
        "positive_reviews": positive,
        "negative_reviews": negative,
        "all_reviews": taught + learned,
        "taught_count": taught,
        "learned_count": learned,
    }


@router.get("/")
async def my_profile(user: CurrentUser, db: DbSession):
    stats = await _review_stats(db, user.id)
    return {"user": UserMe.model_validate(user), "stats": stats}


@router.patch("/", response_model=UserMe)
async def update_profile(payload: ProfileUpdate, user: CurrentUser, db: DbSession):
    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/skills")
async def skills(user: CurrentUser):
    """Skills radar — School21 data, display only."""
    if not user.school21_token_enc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No School21 token stored",
        )
    token = decrypt_token(user.school21_token_enc)
    return await school21_client.get_skills(token, user.school21_login)


@router.get("/{username}", response_model=UserPublic)
async def public_profile(username: str, user: CurrentUser, db: DbSession):
    target = (
        await db.execute(
            select(User).where(User.school21_login == username)
        )
    ).scalar_one_or_none()
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return target
