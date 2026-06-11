"""RequiredChannel DB operations."""
from __future__ import annotations

import uuid

from sqlalchemy import select

from app.db.base import AsyncSessionLocal
from app.db.models.required_channel import RequiredChannel


async def get_all_channels() -> list[RequiredChannel]:
    async with AsyncSessionLocal() as db:
        return list((await db.execute(
            select(RequiredChannel).order_by(RequiredChannel.created_at.desc())
        )).scalars().all())


async def get_active_channels() -> list[RequiredChannel]:
    async with AsyncSessionLocal() as db:
        return list((await db.execute(
            select(RequiredChannel).where(RequiredChannel.is_active.is_(True))
        )).scalars().all())


async def get_channel(channel_uuid: str) -> RequiredChannel | None:
    async with AsyncSessionLocal() as db:
        return await db.get(RequiredChannel, uuid.UUID(channel_uuid))


async def add_channel(channel_id: str, title: str, invite_link: str | None = None) -> RequiredChannel:
    async with AsyncSessionLocal() as db:
        ch = RequiredChannel(channel_id=channel_id, title=title, invite_link=invite_link)
        db.add(ch)
        await db.commit()
        await db.refresh(ch)
        return ch


async def update_channel(channel_uuid: str, **kwargs) -> RequiredChannel | None:
    async with AsyncSessionLocal() as db:
        ch = await db.get(RequiredChannel, uuid.UUID(channel_uuid))
        if not ch:
            return None
        for k, v in kwargs.items():
            setattr(ch, k, v)
        await db.commit()
        await db.refresh(ch)
        return ch


async def toggle_channel(channel_uuid: str) -> RequiredChannel | None:
    async with AsyncSessionLocal() as db:
        ch = await db.get(RequiredChannel, uuid.UUID(channel_uuid))
        if ch:
            ch.is_active = not ch.is_active
            await db.commit()
            await db.refresh(ch)
        return ch


async def delete_channel(channel_uuid: str) -> bool:
    async with AsyncSessionLocal() as db:
        ch = await db.get(RequiredChannel, uuid.UUID(channel_uuid))
        if ch:
            await db.delete(ch)
            await db.commit()
            return True
        return False
