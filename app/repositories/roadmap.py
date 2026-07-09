from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.roadmap import Roadmap, RoadmapChunk


class RoadmapRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        goal_title: str,
        experience: str,
        known_skills: list[str],
        learning_style: str,
        weekly_hours: int,
        roadmap: dict[str, object],
        markdown: str,
    ) -> Roadmap:
        entity = Roadmap(
            goal_title=goal_title,
            experience=experience,
            known_skills=known_skills,
            learning_style=learning_style,
            weekly_hours=weekly_hours,
            roadmap=roadmap,
            markdown=markdown,
        )
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get(self, roadmap_id: str) -> Roadmap:
        result = await self.session.execute(
            select(Roadmap).where(Roadmap.id == roadmap_id).options(selectinload(Roadmap.chunks))
        )
        return result.scalar_one()

    async def add_chunks(
        self, roadmap_id: str, chunks: list[str], embeddings: list[list[float]]
    ) -> list[RoadmapChunk]:
        entities = [
            RoadmapChunk(
                roadmap_id=roadmap_id,
                chunk_index=index,
                content=content,
                embedding=embedding,
            )
            for index, (content, embedding) in enumerate(zip(chunks, embeddings, strict=True))
        ]
        self.session.add_all(entities)
        await self.session.flush()
        return entities

    async def retrieve_chunks(
        self, roadmap_id: str, query_embedding: list[float], limit: int = 5
    ) -> list[RoadmapChunk]:
        distance = RoadmapChunk.embedding.cosine_distance(query_embedding)
        result = await self.session.execute(
            select(RoadmapChunk)
            .where(RoadmapChunk.roadmap_id == roadmap_id)
            .order_by(distance)
            .limit(limit)
        )
        return list(result.scalars().all())
