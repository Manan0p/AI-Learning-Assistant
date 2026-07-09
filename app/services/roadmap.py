from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.prompts.roadmap import ROADMAP_SYSTEM_PROMPT, ROADMAP_USER_PROMPT
from app.repositories.progress import ProgressRepository
from app.repositories.roadmap import RoadmapRepository
from app.schemas.roadmap import RoadmapLLMOutput, RoadmapRequest, RoadmapResponse
from app.services.chunking import ChunkingService
from app.services.gemini import GeminiService
from app.utils.markdown import roadmap_to_markdown


class RoadmapService:
    def __init__(self, session: AsyncSession, gemini: GeminiService) -> None:
        self.session = session
        self.gemini = gemini
        self.roadmaps = RoadmapRepository(session)
        self.progress = ProgressRepository(session)
        self.chunking = ChunkingService()

    async def create(self, request: RoadmapRequest) -> RoadmapResponse:
        schema = RoadmapLLMOutput.model_json_schema()
        prompt = ROADMAP_USER_PROMPT.format(
            goal_title=request.goal_title,
            experience=request.experience,
            known_skills=", ".join(request.known_skills) or "None listed",
            learning_style=request.learning_style,
            weekly_hours=request.weekly_hours,
            schema=schema,
        )
        roadmap = await self.gemini.generate_validated_json(
            system_prompt=ROADMAP_SYSTEM_PROMPT,
            user_prompt=prompt,
            response_model=RoadmapLLMOutput,
            cache_prefix="roadmap",
        )
        markdown = roadmap_to_markdown(roadmap)
        entity = await self.roadmaps.create(
            goal_title=request.goal_title,
            experience=request.experience,
            known_skills=request.known_skills,
            learning_style=request.learning_style,
            weekly_hours=request.weekly_hours,
            roadmap=roadmap.model_dump(mode="json"),
            markdown=markdown,
        )
        chunks = self.chunking.split(markdown)
        embeddings = await self.gemini.embed_documents(chunks)
        await self.roadmaps.add_chunks(entity.id, chunks, embeddings)
        await self.progress.create_for_roadmap(entity.id, [phase.title for phase in roadmap.phases])
        await self.session.commit()
        return RoadmapResponse(roadmap_id=entity.id, roadmap=roadmap)
