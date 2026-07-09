from __future__ import annotations

from pydantic import Field

from app.schemas.common import APIModel


class ChatRequest(APIModel):
    roadmap_id: str = Field(..., examples=["5a71b8db-25ea-41fb-9fc5-86fe9ee4df65"])
    message: str = Field(
        ...,
        min_length=2,
        max_length=2000,
        examples=["What should I learn this week?"],
    )


class ChatLLMOutput(APIModel):
    response: str
    follow_up_questions: list[str] = Field(default_factory=list, max_length=3)


class ChatResponse(ChatLLMOutput):
    retrieved_chunk_ids: list[str]
