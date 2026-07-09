from __future__ import annotations

from pydantic import Field

from app.schemas.common import APIModel, ProgressStatus


class ProgressPatchRequest(APIModel):
    roadmap_id: str
    item_id: str
    status: ProgressStatus = Field(..., examples=["in_progress"])


class ProgressItemResponse(APIModel):
    id: str
    roadmap_id: str
    title: str
    item_type: str
    status: ProgressStatus
    sort_order: int


class ProgressResponse(APIModel):
    roadmap_id: str
    completion_percentage: float
    items: list[ProgressItemResponse]
