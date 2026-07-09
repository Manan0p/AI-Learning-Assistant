from __future__ import annotations

from pydantic import Field, model_validator

from app.schemas.common import APIModel


class ProjectRequest(APIModel):
    roadmap_id: str | None = Field(
        default=None,
        examples=["5a71b8db-25ea-41fb-9fc5-86fe9ee4df65"],
    )
    goal_title: str | None = Field(
        default=None,
        min_length=3,
        max_length=180,
        examples=["Become an AI Engineer"],
    )
    skills: list[str] = Field(
        default_factory=list,
        examples=[["FastAPI", "RAG", "PostgreSQL"]],
    )

    @model_validator(mode="after")
    def validate_source(self) -> ProjectRequest:
        if not self.roadmap_id and not (self.goal_title and self.skills):
            raise ValueError("Provide either roadmap_id or goal_title with skills.")
        return self


class ProjectLLMOutput(APIModel):
    title: str
    difficulty: str
    estimated_hours: int = Field(..., ge=1)
    tech_stack: list[str] = Field(..., min_length=1)
    features: list[str] = Field(..., min_length=3)
    why_this_project: str


class ProjectResponse(APIModel):
    project_id: str
    roadmap_id: str | None
    project: ProjectLLMOutput
