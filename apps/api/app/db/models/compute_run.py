"""ComputeRun ORM model — audit record for every engine invocation."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ComputeRunModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "compute_runs"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("snapshots.id", ondelete="RESTRICT"),
        nullable=False,
    )
    engine: Mapped[str] = mapped_column(String(50), nullable=False)
    function: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    git_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    inputs_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    outputs_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_compute_runs_snapshot_id", "snapshot_id"),
        Index("ix_compute_runs_engine_snapshot", "engine", "snapshot_id"),
        Index("ix_compute_runs_started_at", "started_at"),
    )
