"""Test uchun umumiy fixture va muhit sozlamalari."""

from __future__ import annotations

import os

# Testlar uchun majburiy env o'zgaruvchilarini oldindan o'rnatish.
# (Settings instansiyasi yaratilishidan oldin bajarilishi kerak.)
os.environ.setdefault("BOT_TOKEN", "test:token")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("DEBUG", "True")

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot.database import models  # noqa: F401  (modellarni metadata uchun yuklash)
from bot.database.base import Base


@pytest_asyncio.fixture
async def db_sessionmaker():
    """Har bir test uchun yangi SQLite in-memory baza va session factory."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    try:
        yield maker
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_sessionmaker):
    """Bitta DB sessiyasi (test ichida ishlatish uchun)."""
    async with db_sessionmaker() as session:
        yield session
