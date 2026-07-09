from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.prompts.chat import CHAT_SYSTEM_PROMPT, CHAT_USER_PROMPT
from app.repositories.chat import ChatRepository
from app.repositories.roadmap import RoadmapRepository
from app.schemas.chat import ChatLLMOutput, ChatRequest, ChatResponse
from app.services.gemini import GeminiService


class ChatService:
    def __init__(self, session: AsyncSession, gemini: GeminiService) -> None:
        self.session = session
        self.gemini = gemini
        self.roadmaps = RoadmapRepository(session)
        self.chat = ChatRepository(session)

    async def respond(self, request: ChatRequest) -> ChatResponse:
        await self.roadmaps.get(request.roadmap_id)
        query_embedding = await self.gemini.embed_query(request.message)
        chunks = await self.roadmaps.retrieve_chunks(request.roadmap_id, query_embedding, limit=5)
        context = "\n\n---\n\n".join(chunk.content for chunk in chunks)
        prompt = CHAT_USER_PROMPT.format(
            context=context,
            question=request.message,
            schema=ChatLLMOutput.model_json_schema(),
        )
        answer = await self.gemini.generate_validated_json(
            system_prompt=CHAT_SYSTEM_PROMPT,
            user_prompt=prompt,
            response_model=ChatLLMOutput,
        )
        await self.chat.add_user_message(request.roadmap_id, request.message)
        chunk_ids = [chunk.id for chunk in chunks]
        await self.chat.add_assistant_message(
            roadmap_id=request.roadmap_id,
            content=answer.response,
            follow_up_questions=answer.follow_up_questions,
            retrieved_chunk_ids=chunk_ids,
        )
        await self.session.commit()
        return ChatResponse(
            response=answer.response,
            follow_up_questions=answer.follow_up_questions,
            retrieved_chunk_ids=chunk_ids,
        )
