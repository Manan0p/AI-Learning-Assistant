from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_gemini_service
from app.db.session import get_session
from app.schemas.project import ProjectRequest, ProjectResponse
from app.services.gemini import GeminiService
from app.services.project import ProjectService

router = APIRouter()


@router.post(
    "/project",
    response_model=ProjectResponse,
    summary="Generate and store one roadmap-aligned portfolio project",
)
async def create_project(
    payload: ProjectRequest,
    session: AsyncSession = Depends(get_session),
    gemini: GeminiService = Depends(get_gemini_service),
) -> ProjectResponse:
    return await ProjectService(session, gemini).create(payload)
