"""BotSettings DB operations."""
from __future__ import annotations

from sqlalchemy import select

from app.db.base import AsyncSessionLocal
from app.db.models.bot_settings import BotSettings


async def get_settings() -> BotSettings:
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(BotSettings).where(BotSettings.id == 1))).scalar_one_or_none()
        if s is None:
            s = BotSettings(id=1)
            db.add(s)
            await db.commit()
            await db.refresh(s)
        return s


async def update_settings(**kwargs) -> None:
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(BotSettings).where(BotSettings.id == 1))).scalar_one_or_none()
        if not s:
            s = BotSettings(id=1)
            db.add(s)
        for k, v in kwargs.items():
            setattr(s, k, v)
        await db.commit()
