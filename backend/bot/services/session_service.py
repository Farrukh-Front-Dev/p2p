"""Session (sessiya) servisi — finish oqimi, coin/XP trigger."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.enums import ReviewRole, SessionStatus, SlotStatus
from ..database.models.review import Review
from ..database.models.session import Session
from ..database.models.slot import Slot
from ..database.models.user import User
from ..repositories.session_repo import SessionRepository
from ..repositories.slot_repo import SlotRepository
from ..utils.time_utils import now_local
from .coin_service import CoinService
from .xp_service import XPService


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SessionRepository(db)
        self.slot_repo = SlotRepository(db)

    async def create_session(self, slot: Slot, chat_group_id: int | None = None) -> Session:
        """Slot uchun sessiya yaratadi va slotni active qiladi."""
        session = await self.repo.create(
            slot_id=slot.id,
            mentor_id=slot.mentor_id,
            mentee_id=slot.mentee_id,
            chat_group_id=chat_group_id,
            started_at=now_local(),
            status=SessionStatus.ACTIVE.value,
        )
        await self.slot_repo.update_status(slot.id, SlotStatus.ACTIVE)
        if chat_group_id is not None:
            await self.slot_repo.set_chat_group(slot.id, chat_group_id)
        return session

    async def get_active_session_by_user(self, user_id: int) -> Session | None:
        return await self.repo.get_active_session_by_user(user_id)

    async def submit_finish(
        self,
        session_id: str | uuid.UUID,
        user_id: int,
        comment: str,
        rating: int | None = None,
    ) -> Session | None:
        """Bir tomon yakunlash tasdig'ini saqlaydi.

        Tasdiqlovchini aniqlaydi (mentor/mentee), izoh+baholashni yozadi.
        Ikkala tomon tasdiqlasa: status=finished, coin+XP beriladi (idempotent).
        """
        session = await self.repo.get_by_id(session_id)
        if session is None:
            return None
        if user_id not in (session.mentor_id, session.mentee_id):
            return None

        is_mentor = user_id == session.mentor_id
        reviewer_role = ReviewRole.MENTOR if is_mentor else ReviewRole.MENTEE
        reviewed_id = session.mentee_id if is_mentor else session.mentor_id

        # Tasdiqni belgilash (qayta tasdiqlash zarar qilmaydi)
        if is_mentor:
            if session.mentor_confirmed:
                return session  # allaqachon tasdiqlagan
            session.mentor_confirmed = True
            session.mentor_comment = comment
            session.mentor_rating = rating
        else:
            if session.mentee_confirmed:
                return session
            session.mentee_confirmed = True
            session.mentee_comment = comment
            session.mentee_rating = rating

        if session.finish_requested_by is None:
            session.finish_requested_by = user_id

        # Review yozish
        review = Review(
            session_id=session.id,
            reviewer_id=user_id,
            reviewed_id=reviewed_id,
            rating=rating,
            comment=comment,
            role=reviewer_role.value,
        )
        self.db.add(review)

        # Holatni yangilash
        if session.mentor_confirmed and session.mentee_confirmed:
            session.status = SessionStatus.FINISHED.value
            session.finished_at = now_local()
            await self.db.flush()
            await self._finalize_rewards(session)
            await self.slot_repo.update_status(session.slot_id, SlotStatus.FINISHED)
        else:
            session.status = SessionStatus.FINISHING.value
            await self.db.flush()

        return session

    async def _finalize_rewards(self, session: Session) -> None:
        """Coin + XP berish va reytinglarni yangilash (idempotent)."""
        coin_service = CoinService(self.db)
        xp_service = XPService(self.db)
        await coin_service.reward_mentor(session)
        await xp_service.award_xp(session)
        await self._recompute_rating(session.mentor_id)
        await self._recompute_rating(session.mentee_id)

    async def _recompute_rating(self, user_id: int) -> None:
        """Foydalanuvchi reytingini reviews o'rtachasidan hisoblaydi (avg*20 -> %)."""
        result = await self.db.execute(
            select(func.avg(Review.rating)).where(
                Review.reviewed_id == user_id,
                Review.rating.isnot(None),
            )
        )
        avg = result.scalar()
        if avg is None:
            return
        user = await self.db.get(User, user_id)
        if user is not None:
            user.rating = round(float(avg) * 20, 1)  # 1-5 -> 0-100%
            await self.db.flush()
