from __future__ import annotations

import hashlib

from redis.asyncio import Redis

from app.core.config import settings

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    return _redis


async def close_redis_pool() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


def cache_key(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"
