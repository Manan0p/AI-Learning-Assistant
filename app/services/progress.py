from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.progress import ProgressRepository
from app.repositories.roadmap import RoadmapRepository
from app.schemas.progress import ProgressItemResponse, ProgressPatchRequest, ProgressResponse


class ProgressService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.progress = ProgressRepository(session)
        self.roadmaps = RoadmapRepository(session)

    async def get(self, roadmap_id: str) -> ProgressResponse:
        await self.roadmaps.get(roadmap_id)
        items = await self.progress.list_by_roadmap(roadmap_id)
        completed = sum(1 for item in items if item.status == "completed")
        percentage = round((completed / len(items)) * 100, 2) if items else 0.0
        response_items = [
            ProgressItemResponse.model_validate(item)
            for item in items
        ]
        return ProgressResponse(
            roadmap_id=roadmap_id,
            completion_percentage=percentage,
            items=response_items,
        )

    async def patch(self, request: ProgressPatchRequest) -> ProgressResponse:
        await self.progress.update_status(
            roadmap_id=request.roadmap_id,
            item_id=request.item_id,
            status=request.status,
        )
        await self.session.commit()
        return await self.get(request.roadmap_id)
