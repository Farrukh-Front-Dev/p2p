"""Monthly leaderboard snapshot task."""
from __future__ import annotations

import asyncio
from datetime import date, datetime, timezone

from app.db.base import AsyncSessionLocal
from app.db.models.leaderboard_snapshot import LeaderboardSnapshot
from app.services import leaderboard_service
from app.tasks.celery_app import celery_app


def _previous_month_start() -> date:
    now = datetime.now(timezone.utc)
    year, month = now.year, now.month
    if month == 1:
        return date(year - 1, 12, 1)
    return date(year, month - 1, 1)


@celery_app.task(name="app.tasks.leaderboard_tasks.monthly_snapshot")
def monthly_snapshot() -> int:
    return asyncio.run(_monthly_snapshot())


async def _monthly_snapshot() -> int:
    """Persist the previous month's rankings into LeaderboardSnapshot."""
    month = _previous_month_start()
    written = 0
    async with AsyncSessionLocal() as db:
        categories = {
            leaderboard_service.CATEGORY_MOST_TAUGHT: leaderboard_service.most_taught,
            leaderboard_service.CATEGORY_MOST_LEARNED: leaderboard_service.most_learned,
            leaderboard_service.CATEGORY_MOST_XP: leaderboard_service.most_xp,
        }
        for category, fn in categories.items():
            entries = await fn(db)
            for entry in entries:
                db.add(
                    LeaderboardSnapshot(
                        user_id=entry["user_id"],
                        month=month,
                        category=category,
                        rank=entry["rank"],
                        value=entry["value"],
                    )
                )
                written += 1
        await db.commit()
    return written
