from __future__ import annotations

from app.schemas.roadmap import RoadmapLLMOutput


def roadmap_to_markdown(roadmap: RoadmapLLMOutput) -> str:
    lines = [
        f"# {roadmap.goal_title}",
        "",
        f"Profile: {roadmap.learner_profile}",
        f"Estimated duration: {roadmap.estimated_duration_weeks} weeks",
        f"Recommended cadence: {roadmap.recommended_cadence}",
        "",
        "## Phases",
    ]
    for phase in roadmap.phases:
        lines.extend(
            [
                "",
                f"### {phase.title} ({phase.duration_weeks} weeks)",
                f"Milestone: {phase.milestone}",
                "Objectives:",
                *[f"- {item}" for item in phase.objectives],
                "Skills:",
                *[f"- {item}" for item in phase.skills],
                "Resources:",
                *[f"- {item}" for item in phase.resources],
                "Practice tasks:",
                *[f"- {item}" for item in phase.practice_tasks],
            ]
        )
    lines.extend(["", "## Weekly Plan"])
    for item in roadmap.weekly_plan:
        lines.append(f"- Week {item.week}: {item.focus}. Deliverable: {item.deliverable}")
    lines.extend(["", "## Success Metrics", *[f"- {item}" for item in roadmap.success_metrics]])
    return "\n".join(lines)
