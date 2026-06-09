"""Dashboard endpoint — profile summary + active (booked/in_progress) slots."""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import or_, select

from app.core.dependencies import CurrentUser, DbSession
from app.core.security import decrypt_token
from app.db.models.notification import Notification
from app.db.models.slot import Slot, SlotStatus
from app.schemas.slot import SlotOut
from app.schemas.user import UserMe
from app.services.school21_client import school21_client
from app.services.xp_service import xp_to_next_level

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
async def dashboard(user: CurrentUser, db: DbSession):
    # Real-time location (TTL cache School21 da yo'q, shuning uchun har so'rovda)
    if user.school21_token_enc:
        try:
            token = decrypt_token(user.school21_token_enc)
            workstation = await school21_client.get_location(token, user.school21_login)
            if workstation.get("formatted"):
                user.current_location = workstation["formatted"]
                await db.commit()
        except Exception:
            pass  # location olishda xato — eski qiymat qoladi

    active_stmt = (
        select(Slot)
        .where(
            or_(Slot.reviewer_id == user.id, Slot.reviewee_id == user.id),
            Slot.status.in_(
                [SlotStatus.BOOKED.value, SlotStatus.IN_PROGRESS.value]
            ),
        )
        .order_by(Slot.start_time.asc())
    )
    active_slots = (await db.execute(active_stmt)).scalars().all()

    unread_stmt = select(Notification).where(
        Notification.user_id == user.id, Notification.is_read.is_(False)
    )
    unread = len((await db.execute(unread_stmt)).scalars().all())

    return {
        "user": UserMe.model_validate(user),
        "xp_to_next_level": xp_to_next_level(user.xp),
        "active_slots": [SlotOut.model_validate(s) for s in active_slots],
        "unread_notifications": unread,
    }
