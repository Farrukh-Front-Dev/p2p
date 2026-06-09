"""Slot matching algorithm.

Finds open slots for a selected project, respecting campus / online rules and
language overlap. Tashkent users only see online slots; Samarkand users see
both offline and online slots.
"""
from __future__ import annotations

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.slot import Slot, SlotStatus
from app.db.models.user import User


async def find_matching_slots(
    db: AsyncSession,
    *,
    selected_project: str,
    user_campus: str,
    user_languages: list[str],
) -> list[Slot]:
    stmt = (
        select(Slot)
        .join(User, Slot.reviewer_id == User.id)
        .options(selectinload(Slot.reviewer))
        .where(
            Slot.status == SlotStatus.OPEN.value,
            Slot.reviewer_project == selected_project,
        )
    )

    if user_campus == "tashkent":
        # Tashkent users may only book online slots.
        stmt = stmt.where(Slot.is_online.is_(True))
    else:
        # Samarkand users see same-campus offline slots and any online slot.
        stmt = stmt.where(
            or_(Slot.campus == user_campus, Slot.is_online.is_(True))
        )

    stmt = stmt.order_by(Slot.start_time.asc())

    result = await db.execute(stmt)
    slots = list(result.scalars().all())

    if not user_languages:
        return slots

    # Language overlap filter (reviewer must share at least one language).
    filtered: list[Slot] = []
    langs = set(user_languages)
    for slot in slots:
        reviewer_langs = set(slot.reviewer.languages or [])
        if reviewer_langs & langs:
            filtered.append(slot)
    return filtered
