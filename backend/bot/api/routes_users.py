"""Profil, leaderboard va konstantalar endpointlari."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import DIRECTIONS
from ..database.models.user import User
from ..repositories.user_repo import UserRepository
from .deps import get_current_user, get_db_session
from .schemas import (
    DirectionOut,
    LeaderboardEntry,
    UpdateProfileRequest,
    UserOut,
)
from .serializers import user_to_out

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current: User = Depends(get_current_user)):
    return user_to_out(current)


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: UpdateProfileRequest,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    repo = UserRepository(db)
    fields: dict = {}
    if body.language is not None:
        fields["language"] = body.language
    if body.directions is not None:
        fields["directions"] = body.directions[:5]
    if fields:
        await repo.update(current.id, **fields)
    user = await repo.get_by_id(current.id)
    return user_to_out(user)


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def leaderboard(
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    top = await repo.get_leaderboard(limit=min(limit, 50))
    return [
        LeaderboardEntry(
            rank=i + 1,
            nickname=(("@" + u.username) if u.username else (u.nickname or u.school21_login)),
            xp=u.xp,
            level=u.level,
            total_taught=u.total_taught,
        )
        for i, u in enumerate(top)
    ]


@router.get("/directions", response_model=list[DirectionOut])
async def directions():
    """Yo'nalishlar ro'yxati (autentifikatsiyasiz ham mumkin)."""
    return [DirectionOut(**d) for d in DIRECTIONS]
