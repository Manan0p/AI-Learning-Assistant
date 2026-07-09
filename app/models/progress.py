from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ProgressItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "progress_items"

    roadmap_id: Mapped[str] = mapped_column(
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
