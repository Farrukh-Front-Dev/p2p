"""Leaderboard computation for the current month and historical snapshots."""
from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.leaderboard_snapshot import LeaderboardSnapshot
from app.db.models.slot import Slot, SlotStatus
from app.db.models.user import User
from app.db.models.xp_log import XpLog

CATEGORY_MOST_TAUGHT = "most_taught"
CATEGORY_MOST_LEARNED = "most_learned"
CATEGORY_MOST_XP = "most_xp"


def _month_start(when: datetime | None = None) -> datetime:
    now = when or datetime.now(timezone.utc)
    return datetime(now.year, now.month, 1, tzinfo=timezone.utc)


async def most_taught(db: AsyncSession, limit: int = 50) -> list[dict]:
    start = _month_start()
    stmt = (
        select(
            User.id,
            User.first_name,
            User.last_name,
            func.count(Slot.id).label("value"),
        )
        .join(Slot, Slot.reviewer_id == User.id)
        .where(
            Slot.status == SlotStatus.COMPLETED.value,
            Slot.actual_end >= start,
        )
        .group_by(User.id)
        .order_by(func.count(Slot.id).desc())
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    return [_row_to_entry(i, r) for i, r in enumerate(rows, start=1)]


async def most_learned(db: AsyncSession, limit: int = 50) -> list[dict]:
    start = _month_start()
    stmt = (
        select(
            User.id,
            User.first_name,
            User.last_name,
            func.count(Slot.id).label("value"),
        )
        .join(Slot, Slot.reviewee_id == User.id)
        .where(
            Slot.status == SlotStatus.COMPLETED.value,
            Slot.actual_end >= start,
        )
        .group_by(User.id)
        .order_by(func.count(Slot.id).desc())
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    return [_row_to_entry(i, r) for i, r in enumerate(rows, start=1)]


async def most_xp(db: AsyncSession, limit: int = 50) -> list[dict]:
    start = _month_start()
    stmt = (
        select(
            User.id,
            User.first_name,
            User.last_name,
            func.coalesce(func.sum(XpLog.amount), 0).label("value"),
        )
        .join(XpLog, XpLog.user_id == User.id)
        .where(XpLog.created_at >= start)
        .group_by(User.id)
        .order_by(func.coalesce(func.sum(XpLog.amount), 0).desc())
        .limit(limit)
    )
    rows = (await db.execute(stmt)).all()
    return [_row_to_entry(i, r) for i, r in enumerate(rows, start=1)]


def _row_to_entry(rank: int, row) -> dict:
    return {
        "rank": rank,
        "user_id": str(row[0]),
        "first_name": row[1],
        "last_name": row[2],
        "value": int(row[3]),
    }


async def get_history(
    db: AsyncSession, month: date, category: str
) -> list[dict]:
    stmt = (
        select(LeaderboardSnapshot)
        .where(
            LeaderboardSnapshot.month == month,
            LeaderboardSnapshot.category == category,
        )
        .order_by(LeaderboardSnapshot.rank.asc())
    )
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "rank": s.rank,
            "user_id": str(s.user_id),
            "value": s.value,
        }
        for s in rows
    ]
