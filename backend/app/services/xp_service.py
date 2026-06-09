"""Platform-internal XP & Level logic. Fully independent from School21."""
from __future__ import annotations

import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.models.xp_log import XpLog


def get_level(xp: int) -> int:
    """Compute level from XP."""
    return int(math.sqrt(max(xp, 0) / 100))


def xp_for_level(n: int) -> int:
    """Minimal XP required to reach level N."""
    return 100 * n * n


def xp_to_next_level(xp: int) -> int:
    """How much XP remains to the next level."""
    current = get_level(xp)
    return xp_for_level(current + 1) - xp


async def apply_xp(
    db: AsyncSession,
    user: User,
    amount: int,
    reason: str,
    slot_id: uuid.UUID | None = None,
) -> None:
    """Atomically apply an XP change, recompute level and write an XpLog."""
    new_xp = max(user.xp + amount, 0)
    user.xp = new_xp
    user.level = get_level(new_xp)
    db.add(
        XpLog(user_id=user.id, amount=amount, reason=reason, slot_id=slot_id)
    )
