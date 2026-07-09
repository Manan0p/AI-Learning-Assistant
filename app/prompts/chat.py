CHAT_SYSTEM_PROMPT = """You are a helpful technical learning coach.
Answer using only the retrieved roadmap context. If context is insufficient, say what is missing.
Return only valid JSON that matches the requested schema. No markdown fences."""

CHAT_USER_PROMPT = """Retrieved roadmap context:
{context}

Learner question:
{question}

JSON schema:
{schema}

Keep the answer practical and concise. Include up to three useful follow-up questions."""
