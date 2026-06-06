"""Async DB engine va session factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..config import settings

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Yagona (singleton) async engine qaytaradi."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.SQL_ECHO,
            pool_pre_ping=True,
        )
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Session factory qaytaradi."""
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _sessionmaker


def configure_sessionmaker(maker: async_sessionmaker[AsyncSession]) -> None:
    """Test uchun: session factory ni almashtirish (masalan SQLite)."""
    global _sessionmaker
    _sessionmaker = maker


@asynccontextmanager
async def get_db() -> AsyncIterator[AsyncSession]:
    """DB sessiyasini context manager sifatida beradi.

    Muvaffaqiyatda commit, xatoda rollback qiladi.
    """
    maker = get_sessionmaker()
    async with maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
