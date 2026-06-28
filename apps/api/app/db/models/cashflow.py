"""Cashflow ORM models — contractual and behavioral cashflow projections."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

MONEY = Numeric(precision=28, scale=8)


class CashflowModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Contractual cashflow schedule per position within a snapshot.
    Partitioned by cashflow_date for query efficiency over time horizons.
    """

    __tablename__ = "cashflows"

    position_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    position_reporting_date: Mapped[date] = mapped_column(Date, nullable=False)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("snapshots.id", ondelete="RESTRICT"),
        nullable=False,
    )
    cashflow_type: Mapped[str] = mapped_column(String(30), nullable=False)
    cashflow_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    is_contractual: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    time_bucket: Mapped[str | None] = mapped_column(String(20), nullable=True)

    __table_args__ = (
        Index("ix_cashflows_position_id", "position_id"),
        Index("ix_cashflows_snapshot_id", "snapshot_id"),
        Index("ix_cashflows_date", "cashflow_date"),
        Index("ix_cashflows_time_bucket", "time_bucket"),
    )


class CashflowProjectionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Aggregated cashflow projection per time bucket for LCR/NSFR/SLS computation."""

    __tablename__ = "cashflow_projections"

    position_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    position_reporting_date: Mapped[date] = mapped_column(Date, nullable=False)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("snapshots.id", ondelete="RESTRICT"),
        nullable=False,
    )
    scenario_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    projection_type: Mapped[str] = mapped_column(String(30), nullable=False)
    time_bucket: Mapped[str] = mapped_column(String(20), nullable=False)
    inflow_amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    outflow_amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    __table_args__ = (
        Index("ix_cf_proj_position_snapshot", "position_id", "snapshot_id"),
        Index("ix_cf_proj_scenario_id", "scenario_id"),
        Index("ix_cf_proj_time_bucket", "time_bucket"),
        Index("ix_cf_proj_type", "projection_type"),
    )
