"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-09 10:30:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "roadmaps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("goal_title", sa.String(length=180), nullable=False),
        sa.Column("experience", sa.String(length=120), nullable=False),
        sa.Column("known_skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("learning_style", sa.String(length=120), nullable=False),
        sa.Column("weekly_hours", sa.Integer(), nullable=False),
        sa.Column("roadmap", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("markdown", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("roadmap_id", sa.UUID(), nullable=True),
        sa.Column("goal_title", sa.String(length=180), nullable=False),
        sa.Column("project", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["roadmap_id"], ["roadmaps.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "roadmap_chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("roadmap_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(dim=768), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["roadmap_id"], ["roadmaps.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("roadmap_id", "chunk_index", name="uq_roadmap_chunk_index"),
    )
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("roadmap_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("follow_up_questions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("retrieved_chunk_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["roadmap_id"], ["roadmaps.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "progress_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("roadmap_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("item_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["roadmap_id"], ["roadmaps.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chunks_roadmap_id", "roadmap_chunks", ["roadmap_id"])
    op.create_index(
        "ix_chunks_embedding_hnsw",
        "roadmap_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_chunks_embedding_hnsw", table_name="roadmap_chunks")
    op.drop_index("ix_chunks_roadmap_id", table_name="roadmap_chunks")
    op.drop_table("progress_items")
    op.drop_table("chat_messages")
    op.drop_table("roadmap_chunks")
    op.drop_table("projects")
    op.drop_table("roadmaps")
