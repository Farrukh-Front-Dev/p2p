"""Session repository."""

from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.enums import SessionStatus
from ..database.models.session import Session


def _to_uuid(value: str | uuid.UUID) -> uuid.UUID:
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


# Faol hisoblangan statuslar
_ACTIVE_STATUSES = (SessionStatus.ACTIVE.value, SessionStatus.FINISHING.value)


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> Session:
        session = Session(**kwargs)
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_by_id(self, session_id: str | uuid.UUID) -> Session | None:
        return await self.db.get(Session, _to_uuid(session_id))

    async def get_active_session_by_user(self, user_id: int) -> Session | None:
        """Foydalanuvchining faol (active/finishing) sessiyasini qaytaradi."""
        result = await self.db.execute(
            select(Session)
            .where(
                or_(
                    Session.mentor_id == user_id,
                    Session.mentee_id == user_id,
                ),
                Session.status.in_(_ACTIVE_STATUSES),
            )
            .order_by(Session.created_at.desc())
        )
        return result.scalars().first()
