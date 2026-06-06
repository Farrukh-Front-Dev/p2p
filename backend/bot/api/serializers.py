"""ORM -> API sxema konvertorlari."""

from __future__ import annotations

from ..database.models.slot import Slot
from ..database.models.user import User
from ..utils.level_utils import get_level_info
from .schemas import SlotOut, UserOut


def user_to_out(user: User) -> UserOut:
    info = get_level_info(user.xp)
    return UserOut(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        school21_login=user.school21_login,
        language=user.language,
        directions=list(user.directions or []),
        coins=user.coins,
        max_coins=user.max_coins,
        xp=user.xp,
        level=info["level"],
        level_name=info["name"],
        level_progress=info["progress"],
        xp_to_next=info["xp_needed"],
        rating=user.rating,
        total_taught=user.total_taught,
        total_learned=user.total_learned,
    )


def slot_to_out(slot: Slot, current_user_id: int | None = None) -> SlotOut:
    role = None
    is_mine = False
    if current_user_id is not None:
        if slot.mentor_id == current_user_id:
            role = "mentor"
            is_mine = True
        elif slot.mentee_id == current_user_id:
            role = "mentee"
            is_mine = True
    return SlotOut(
        id=str(slot.id),
        direction=slot.direction,
        title=slot.title,
        start_time=slot.start_time,
        end_time=slot.end_time,
        status=slot.status,
        is_mine=is_mine,
        role=role,
    )
