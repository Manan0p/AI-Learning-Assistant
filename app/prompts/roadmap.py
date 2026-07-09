ROADMAP_SYSTEM_PROMPT = """You are an expert technical mentor and career coach.
Return only valid JSON that matches the requested schema. No markdown fences."""

ROADMAP_USER_PROMPT = """Create a personalized learning roadmap.

Learner:
- Goal title: {goal_title}
- Experience: {experience}
- Known skills: {known_skills}
- Learning style: {learning_style}
- Weekly hours: {weekly_hours}

JSON schema:
{schema}

Make the roadmap realistic, internship-assignment friendly, and portfolio-oriented.
Use concrete resources and measurable milestones."""
