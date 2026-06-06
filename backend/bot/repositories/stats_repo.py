"""Admin statistika repository."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.enums import SessionStatus, SlotStatus
from ..database.models.session import Session
from ..database.models.slot import Slot
from ..database.models.user import User


class StatsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _count(self, model, *where) -> int:
        stmt = select(func.count()).select_from(model)
        if where:
            stmt = stmt.where(*where)
        return (await self.db.execute(stmt)).scalar() or 0

    async def gather(self) -> dict:
        users = await self._count(User)
        slots = await self._count(Slot)
        open_slots = await self._count(Slot, Slot.status == SlotStatus.OPEN.value)
        sessions = await self._count(Session)
        finished = await self._count(Session, Session.status == SessionStatus.FINISHED.value)
        total_coins = (
            await self.db.execute(select(func.coalesce(func.sum(User.coins), 0)))
        ).scalar() or 0
        return {
            "users": users,
            "slots": slots,
            "open_slots": open_slots,
            "sessions": sessions,
            "finished": finished,
            "coins": total_coins,
        }

    async def all_user_ids(self) -> list[int]:
        result = await self.db.execute(select(User.id).where(User.is_active.is_(True)))
        return [row[0] for row in result.all()]
