from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import chat, health, progress, project, roadmap

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(roadmap.router, tags=["roadmap"])
api_router.include_router(project.router, tags=["project"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(progress.router, tags=["progress"])
