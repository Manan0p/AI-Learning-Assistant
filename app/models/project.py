from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    roadmap_id: Mapped[str | None] = mapped_column(ForeignKey("roadmaps.id", ondelete="SET NULL"))
    goal_title: Mapped[str] = mapped_column(String(180), nullable=False)
    project: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
