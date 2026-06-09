"""Async Redis client wrapper used for caching and pub/sub."""
from __future__ import annotations

import redis.asyncio as aioredis

from app.core.config import settings

redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL, encoding="utf-8", decode_responses=True
)


async def close_redis() -> None:
    await redis_client.aclose()
