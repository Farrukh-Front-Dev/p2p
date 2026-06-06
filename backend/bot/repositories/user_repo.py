"""User repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_login(self, school21_login: str) -> User | None:
        result = await self.db.execute(select(User).where(User.school21_login == school21_login))
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        user_id: int,
        username: str | None,
        school21_login: str,
        nickname: str | None,
        avatar_url: str | None = None,
        directions: list[str] | None = None,
        language: str = "uz",
        level: int = 1,
        xp: int = 0,
    ) -> User:
        """Foydalanuvchini yaratadi yoki mavjudini yangilaydi (ro'yxatdan o'tish)."""
        user = await self.get_by_id(user_id)
        if user is None:
            user = User(
                id=user_id,
                username=username,
                school21_login=school21_login,
                nickname=nickname,
                avatar_url=avatar_url,
                directions=directions or [],
                language=language,
                level=level,
                xp=xp,
                coins=settings.DEFAULT_COINS,
                max_coins=settings.MAX_COINS,
                is_active=True,
            )
            self.db.add(user)
        else:
            user.username = username
            user.school21_login = school21_login
            user.nickname = nickname
            if avatar_url is not None:
                user.avatar_url = avatar_url
            if directions is not None:
                user.directions = directions
            user.language = language
            user.is_active = True
        await self.db.flush()
        return user

    async def update(self, user_id: int, **fields) -> User | None:
        """Foydalanuvchi maydonlarini yangilaydi."""
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        for key, value in fields.items():
            setattr(user, key, value)
        await self.db.flush()
        return user

    async def set_language(self, user_id: int, language: str) -> None:
        await self.update(user_id, language=language)

    async def get_leaderboard(self, limit: int = 10) -> list[User]:
        """XP bo'yicha eng yuqori foydalanuvchilar (reyting jadvali)."""
        result = await self.db.execute(
            select(User)
            .where(User.is_active.is_(True))
            .order_by(User.xp.desc(), User.total_taught.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
