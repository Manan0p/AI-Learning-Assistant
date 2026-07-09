from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.progress import ProgressPatchRequest, ProgressResponse
from app.services.progress import ProgressService

router = APIRouter()


@router.get(
    "/progress",
    response_model=ProgressResponse,
    summary="Get roadmap completion status",
)
async def get_progress(
    roadmap_id: str = Query(...),
    session: AsyncSession = Depends(get_session),
) -> ProgressResponse:
    return await ProgressService(session).get(roadmap_id)


@router.patch(
    "/progress",
    response_model=ProgressResponse,
    summary="Update a roadmap progress item",
)
async def patch_progress(
    payload: ProgressPatchRequest,
    session: AsyncSession = Depends(get_session),
) -> ProgressResponse:
    return await ProgressService(session).patch(payload)
