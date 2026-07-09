from __future__ import annotations

from pydantic import Field

from app.schemas.common import APIModel


class RoadmapRequest(APIModel):
    goal_title: str = Field(
        ...,
        min_length=3,
        max_length=180,
        examples=["Become an AI Engineer"],
    )
    experience: str = Field(
        ...,
        min_length=2,
        max_length=120,
        examples=["Beginner Python developer"],
    )
    known_skills: list[str] = Field(
        default_factory=list,
        examples=[["Python", "SQL", "basic ML"]],
    )
    learning_style: str = Field(
        ...,
        min_length=2,
        max_length=120,
        examples=["Project-based"],
    )
    weekly_hours: int = Field(..., ge=1, le=80, examples=[10])


class RoadmapPhase(APIModel):
    title: str
    duration_weeks: int = Field(..., ge=1)
    objectives: list[str] = Field(..., min_length=1)
    skills: list[str] = Field(..., min_length=1)
    resources: list[str] = Field(..., min_length=1)
    practice_tasks: list[str] = Field(..., min_length=1)
    milestone: str


class WeeklyPlanItem(APIModel):
    week: int = Field(..., ge=1)
    focus: str
    deliverable: str


class RoadmapLLMOutput(APIModel):
    goal_title: str
    learner_profile: str
    estimated_duration_weeks: int = Field(..., ge=1)
    phases: list[RoadmapPhase] = Field(..., min_length=2)
    weekly_plan: list[WeeklyPlanItem] = Field(..., min_length=1)
    success_metrics: list[str] = Field(..., min_length=1)
    recommended_cadence: str


class RoadmapResponse(APIModel):
    roadmap_id: str
    roadmap: RoadmapLLMOutput
