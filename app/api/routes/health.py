from __future__ import annotations

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_redis_client
from app.db.session import get_session
from app.schemas.health import HealthResponse
from app.services.health import HealthService

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Check API dependencies")
async def health(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_client),
) -> HealthResponse:
    return await HealthService(session, redis).check()
