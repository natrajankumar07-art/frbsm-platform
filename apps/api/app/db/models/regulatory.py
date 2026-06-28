"""Regulatory history and filing ORM models — parameter changes, filings, and lineage."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

MONEY = Numeric(precision=28, scale=8)
RATE = Numeric(precision=20, scale=8)


class RegulatoryParameterHistoryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Append-only history of changes to regulatory reference parameters."""

    __tablename__ = "regulatory_parameter_history"

    parameter_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parameter_key: Mapped[str] = mapped_column(String(200), nullable=False)
    old_value: Mapped[Decimal | None] = mapped_column(RATE, nullable=True)
    new_value: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    changed_by: Mapped[str] = mapped_column(String(200), nullable=False)
    regulatory_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(10), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_reg_param_hist_type_key", "parameter_type", "parameter_key"),
        Index("ix_reg_param_hist_effective", "effective_from"),
        Index("ix_reg_param_hist_jurisdiction", "jurisdiction"),
    )


class RegulatoryFilingModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Metadata record for a filed regulatory return."""

    __tablename__ = "regulatory_filings"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("snapshots.id", ondelete="RESTRICT"),
        nullable=False,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    return_type: Mapped[str] = mapped_column(String(50), nullable=False)
    filing_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    filed_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    filed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    filing_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_reg_filings_snapshot_entity", "snapshot_id", "entity_id"),
        Index("ix_reg_filings_return_type", "return_type"),
        Index("ix_reg_filings_period_end", "period_end"),
        Index("ix_reg_filings_status", "status"),
    )


class RegulatoryFilingLineageModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Line-item-level lineage trace — every filed number to its compute run."""

    __tablename__ = "regulatory_filing_lineage"

    filing_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("regulatory_filings.id", ondelete="CASCADE"),
        nullable=False,
    )
    compute_run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("compute_runs.id", ondelete="RESTRICT"),
        nullable=False,
    )
    line_item_code: Mapped[str] = mapped_column(String(100), nullable=False)
    line_item_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    value: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    __table_args__ = (
        Index("ix_reg_lineage_filing_id", "filing_id"),
        Index("ix_reg_lineage_compute_run_id", "compute_run_id"),
        Index("ix_reg_lineage_line_item", "line_item_code"),
    )
