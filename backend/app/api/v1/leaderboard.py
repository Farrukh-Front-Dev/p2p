"""Leaderboard endpoints."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DbSession
from app.services import leaderboard_service

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/most-taught")
async def most_taught(user: CurrentUser, db: DbSession):
    return await leaderboard_service.most_taught(db)


@router.get("/most-learned")
async def most_learned(user: CurrentUser, db: DbSession):
    return await leaderboard_service.most_learned(db)


@router.get("/most-xp")
async def most_xp(user: CurrentUser, db: DbSession):
    return await leaderboard_service.most_xp(db)


@router.get("/history")
async def history(
    user: CurrentUser,
    db: DbSession,
    month: date = Query(...),
    category: str = Query("most_xp"),
):
    return await leaderboard_service.get_history(db, month, category)
