PROJECT_SYSTEM_PROMPT = """You design realistic portfolio projects for AI engineering learners.
Return only valid JSON that matches the requested schema. No markdown fences."""

PROJECT_USER_PROMPT = """Generate exactly one portfolio project.

Context:
{context}

JSON schema:
{schema}

The project must be achievable, specific, and aligned with the learner's roadmap or skills."""
