from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.prompts.project import PROJECT_SYSTEM_PROMPT, PROJECT_USER_PROMPT
from app.repositories.project import ProjectRepository
from app.repositories.roadmap import RoadmapRepository
from app.schemas.project import ProjectLLMOutput, ProjectRequest, ProjectResponse
from app.services.gemini import GeminiService


class ProjectService:
    def __init__(self, session: AsyncSession, gemini: GeminiService) -> None:
        self.session = session
        self.gemini = gemini
        self.projects = ProjectRepository(session)
        self.roadmaps = RoadmapRepository(session)

    async def create(self, request: ProjectRequest) -> ProjectResponse:
        roadmap_id = request.roadmap_id
        if roadmap_id:
            roadmap = await self.roadmaps.get(roadmap_id)
            goal_title = roadmap.goal_title
            context = roadmap.markdown
        else:
            goal_title = request.goal_title or "Portfolio project"
            context = f"Goal: {goal_title}\nSkills: {', '.join(request.skills)}"

        prompt = PROJECT_USER_PROMPT.format(
            context=context,
            schema=ProjectLLMOutput.model_json_schema(),
        )
        project = await self.gemini.generate_validated_json(
            system_prompt=PROJECT_SYSTEM_PROMPT,
            user_prompt=prompt,
            response_model=ProjectLLMOutput,
            cache_prefix="project",
        )
        entity = await self.projects.create(
            roadmap_id=roadmap_id,
            goal_title=goal_title,
            project=project.model_dump(mode="json"),
        )
        await self.session.commit()
        return ProjectResponse(project_id=entity.id, roadmap_id=roadmap_id, project=project)
