from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_gemini_service
from app.db.session import get_session
from app.schemas.roadmap import RoadmapRequest, RoadmapResponse
from app.services.gemini import GeminiService
from app.services.roadmap import RoadmapService

router = APIRouter()


@router.post(
    "/roadmap",
    response_model=RoadmapResponse,
    summary="Generate and store a personalized learning roadmap",
)
async def create_roadmap(
    payload: RoadmapRequest,
    session: AsyncSession = Depends(get_session),
    gemini: GeminiService = Depends(get_gemini_service),
) -> RoadmapResponse:
    return await RoadmapService(session, gemini).create(payload)
