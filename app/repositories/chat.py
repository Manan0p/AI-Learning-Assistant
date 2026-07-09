from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_user_message(self, roadmap_id: str, content: str) -> ChatMessage:
        entity = ChatMessage(roadmap_id=roadmap_id, role="user", content=content)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def add_assistant_message(
        self,
        *,
        roadmap_id: str,
        content: str,
        follow_up_questions: list[str],
        retrieved_chunk_ids: list[str],
    ) -> ChatMessage:
        entity = ChatMessage(
            roadmap_id=roadmap_id,
            role="assistant",
            content=content,
            follow_up_questions=follow_up_questions,
            retrieved_chunk_ids=retrieved_chunk_ids,
        )
        self.session.add(entity)
        await self.session.flush()
        return entity
