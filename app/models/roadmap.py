from __future__ import annotations

from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Roadmap(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roadmaps"

    goal_title: Mapped[str] = mapped_column(String(180), nullable=False)
    experience: Mapped[str] = mapped_column(String(120), nullable=False)
    known_skills: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    learning_style: Mapped[str] = mapped_column(String(120), nullable=False)
    weekly_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    roadmap: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    markdown: Mapped[str] = mapped_column(Text, nullable=False)

    chunks: Mapped[list[RoadmapChunk]] = relationship(
        back_populates="roadmap", cascade="all, delete-orphan", passive_deletes=True
    )


class RoadmapChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roadmap_chunks"
    __table_args__ = (UniqueConstraint("roadmap_id", "chunk_index", name="uq_roadmap_chunk_index"),)

    roadmap_id: Mapped[str] = mapped_column(
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(768), nullable=False)

    roadmap: Mapped[Roadmap] = relationship(back_populates="chunks")
