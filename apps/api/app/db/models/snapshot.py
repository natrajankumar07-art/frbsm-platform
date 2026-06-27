"""Snapshot ORM model."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SnapshotModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "snapshots"

    reporting_date: Mapped[date] = mapped_column(Date, nullable=False)
    frozen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    frozen_by: Mapped[str] = mapped_column(String(200), nullable=False)  # user_id
    position_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 hex
    reference_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    position_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="draft")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_snapshots_reporting_date", "reporting_date"),
        Index("ix_snapshots_status", "status"),
    )
