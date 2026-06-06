"""XP va level servisi — idempotent."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database.models.session import Session
from ..database.models.user import User
from ..utils.level_utils import calculate_level


class XPService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def award_xp(self, session: Session) -> dict | None:
        """Sessiya uchun XP beradi (idempotent: xp_awarded bayrog'i).

        Mentor +XP_PER_SESSION & total_taught++, mentee +XP_PER_SESSION/2 &
        total_learned++. Level qayta hisoblanadi (Property 10).
        Qaytaradi: level-up ma'lumotlari yoki None (allaqachon berilgan bo'lsa).
        """
        if session.xp_awarded:
            return None

        mentor_xp = settings.XP_PER_SESSION
        mentee_xp = settings.XP_PER_SESSION // 2

        mentor = await self.db.get(User, session.mentor_id)
        mentee = await self.db.get(User, session.mentee_id)
        if mentor is None or mentee is None:
            return None

        mentor_old_level = mentor.level
        mentor.xp += mentor_xp
        mentor.level = calculate_level(mentor.xp)
        mentor.total_taught += 1

        mentee_old_level = mentee.level
        mentee.xp += mentee_xp
        mentee.level = calculate_level(mentee.xp)
        mentee.total_learned += 1

        session.xp_awarded = True
        await self.db.flush()

        return {
            "mentor_xp_gained": mentor_xp,
            "mentee_xp_gained": mentee_xp,
            "mentor_leveled_up": mentor.level > mentor_old_level,
            "mentee_leveled_up": mentee.level > mentee_old_level,
            "mentor_level": mentor.level,
            "mentee_level": mentee.level,
        }
