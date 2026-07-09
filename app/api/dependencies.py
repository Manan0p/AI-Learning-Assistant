from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.cache import get_redis
from app.services.gemini import GeminiService


async def get_gemini_service() -> GeminiService:
    return GeminiService()


async def get_redis_client() -> AsyncIterator[Redis]:
    yield await get_redis()


SessionDep = Depends(get_session)
GeminiDep = Depends(get_gemini_service)
RedisDep = Depends(get_redis_client)
