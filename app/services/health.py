from __future__ import annotations

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.health import HealthResponse


class HealthService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.redis = redis

    async def check(self) -> HealthResponse:
        database = "ok"
        redis_status = "ok"
        try:
            await self.session.execute(text("SELECT 1"))
        except Exception:
            database = "unavailable"
        try:
            await self.redis.ping()
        except Exception:
            redis_status = "unavailable"
        overall = "ok" if database == redis_status == "ok" else "degraded"
        return HealthResponse(status=overall, database=database, redis=redis_status)
