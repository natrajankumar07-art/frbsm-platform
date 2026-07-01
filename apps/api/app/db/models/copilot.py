"""ORM models for AI Copilot sessions and messages."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CopilotSessionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "copilot_sessions"

    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("legal_entities.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_id: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    __table_args__ = (
        Index("ix_copilot_sessions_entity_id", "entity_id"),
    )


class CopilotMessageModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "copilot_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("copilot_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("snapshots.id", ondelete="SET NULL"),
        nullable=True,
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("legal_entities.id", ondelete="SET NULL"),
        nullable=True,
    )
    context_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tokens_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("ix_copilot_messages_session_id", "session_id"),
    )
