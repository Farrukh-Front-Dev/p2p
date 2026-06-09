"""Notification persistence + Telegram dispatch trigger."""
from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    user_id: uuid.UUID,
    type_: str,
    title: str | None = None,
    body: str | None = None,
    slot_id: uuid.UUID | None = None,
) -> Notification:
    """Persist a notification row. Telegram delivery is handled by Celery."""
    notif = Notification(
        user_id=user_id,
        type=type_,
        title=title,
        body=body,
        slot_id=slot_id,
    )
    db.add(notif)
    await db.flush()
    return notif
