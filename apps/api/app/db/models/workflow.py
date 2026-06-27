"""Workflow ORM models — workpapers, sign-offs, close calendar tasks."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class WorkpaperModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workpapers"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("snapshots.id", ondelete="RESTRICT"),
        nullable=False,
    )
    return_code: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "RBI_DSB_I"
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    preparer_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approver_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA-256 at approval
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_workpapers_snapshot_id", "snapshot_id"),
        Index("ix_workpapers_status", "status"),
    )


class SignOffModel(UUIDPrimaryKeyMixin, Base):
    """Electronic attestation — immutable once created."""

    __tablename__ = "sign_offs"

    workpaper_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workpapers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(String(200), nullable=False)
    user_role: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # prepared|reviewed|approved
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        Index("ix_sign_offs_workpaper_id", "workpaper_id"),
        Index("ix_sign_offs_user_id", "user_id"),
    )


class CloseTaskModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "close_tasks"

    period: Mapped[str] = mapped_column(String(20), nullable=False)   # "2026-03-31"
    period_type: Mapped[str] = mapped_column(String(10), nullable=False)  # month_end|quarter_end
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_role: Mapped[str] = mapped_column(String(20), nullable=False)
    owner_user_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    depends_on: Mapped[list[uuid.UUID]] = mapped_column(
        # JSON array of CloseTask UUIDs (stored as text to avoid circular FK)
        Text,
        nullable=False,
        default="[]",
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("ix_close_tasks_period", "period"),
        Index("ix_close_tasks_status", "status"),
    )
