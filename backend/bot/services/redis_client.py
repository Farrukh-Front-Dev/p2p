"""Redis klient (singleton)."""

from __future__ import annotations

import redis.asyncio as aioredis

from ..config import settings

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    """Yagona async Redis klientini qaytaradi."""
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


def set_redis(client: aioredis.Redis) -> None:
    """Test uchun: Redis klientini almashtirish (masalan fakeredis)."""
    global _redis
    _redis = client


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
