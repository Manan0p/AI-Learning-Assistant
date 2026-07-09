from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_gemini_service
from app.db.session import get_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService
from app.services.gemini import GeminiService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="Ask a RAG-grounded roadmap question")
async def chat(
    payload: ChatRequest,
    session: AsyncSession = Depends(get_session),
    gemini: GeminiService = Depends(get_gemini_service),
) -> ChatResponse:
    return await ChatService(session, gemini).respond(payload)
