from __future__ import annotations

from app.schemas.roadmap import RoadmapLLMOutput
from app.utils.markdown import roadmap_to_markdown


def test_roadmap_to_markdown_contains_retrievable_sections() -> None:
    roadmap = RoadmapLLMOutput(
        goal_title="AI Engineer",
        learner_profile="Beginner with Python",
        estimated_duration_weeks=8,
        phases=[
            {
                "title": "Foundations",
                "duration_weeks": 2,
                "objectives": ["Learn APIs"],
                "skills": ["FastAPI"],
                "resources": ["FastAPI docs"],
                "practice_tasks": ["Build CRUD API"],
                "milestone": "Deploy an API",
            },
            {
                "title": "RAG",
                "duration_weeks": 2,
                "objectives": ["Learn retrieval"],
                "skills": ["Embeddings"],
                "resources": ["pgvector docs"],
                "practice_tasks": ["Build vector search"],
                "milestone": "Answer with citations",
            },
        ],
        weekly_plan=[{"week": 1, "focus": "APIs", "deliverable": "Working endpoint"}],
        success_metrics=["Can explain RAG"],
        recommended_cadence="Five focused sessions per week",
    )

    markdown = roadmap_to_markdown(roadmap)

    assert "# AI Engineer" in markdown
    assert "## Phases" in markdown
    assert "### RAG" in markdown
    assert "## Weekly Plan" in markdown
