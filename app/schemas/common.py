from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ProgressStatus(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
