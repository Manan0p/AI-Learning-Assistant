from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, *, roadmap_id: str | None, goal_title: str, project: dict[str, Any]
    ) -> Project:
        entity = Project(roadmap_id=roadmap_id, goal_title=goal_title, project=project)
        self.session.add(entity)
        await self.session.flush()
        return entity
