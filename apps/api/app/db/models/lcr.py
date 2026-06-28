"""LCR (Liquidity Coverage Ratio) result ORM models per Basel III LCR standard."""

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

MONEY = Numeric(precision=28, scale=8)
RATE = Numeric(precision=10, scale=6)


class LCRResultModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Top-level LCR computation result for a snapshot/entity pair."""

    __tablename__ = "lcr_results"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("snapshots.id", ondelete="RESTRICT"),
        nullable=False,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    compute_run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("compute_runs.id", ondelete="RESTRICT"),
        nullable=False,
    )
    hqla_total: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    net_cash_outflows: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    total_outflows: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    total_inflows: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    inflow_cap_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    lcr_ratio: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    minimum_ratio: Mapped[Decimal] = mapped_column(RATE, nullable=False, default=Decimal("1.0"))
    passes: Mapped[bool] = mapped_column(Boolean, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    __table_args__ = (
        UniqueConstraint("snapshot_id", "entity_id", name="uq_lcr_snapshot_entity"),
        Index("ix_lcr_snapshot_entity", "snapshot_id", "entity_id"),
        Index("ix_lcr_compute_run", "compute_run_id"),
        Index("ix_lcr_passes", "passes"),
    )


class LCRHQLAComponentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """HQLA breakdown per level and asset class for a LCR result."""

    __tablename__ = "lcr_hqla_components"

    lcr_result_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("lcr_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    hqla_level: Mapped[str] = mapped_column(String(20), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(50), nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    haircut_rate: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    cap_applies: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("ix_lcr_hqla_result_id", "lcr_result_id"),
        Index("ix_lcr_hqla_level", "hqla_level"),
    )


class LCROutflowComponentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Cash outflow component breakdown for a LCR result (LCR40)."""

    __tablename__ = "lcr_outflow_components"

    lcr_result_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("lcr_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    outflow_category: Mapped[str] = mapped_column(String(100), nullable=False)
    deposit_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    customer_segment: Mapped[str | None] = mapped_column(String(30), nullable=True)
    gross_outflow: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    run_off_rate: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    net_outflow: Mapped[Decimal] = mapped_column(MONEY, nullable=False)

    __table_args__ = (
        Index("ix_lcr_outflow_result_id", "lcr_result_id"),
        Index("ix_lcr_outflow_category", "outflow_category"),
    )


class LCRInflowComponentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Cash inflow component breakdown for a LCR result (LCR40)."""

    __tablename__ = "lcr_inflow_components"

    lcr_result_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("lcr_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    inflow_category: Mapped[str] = mapped_column(String(100), nullable=False)
    asset_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gross_inflow: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    inflow_rate: Mapped[Decimal] = mapped_column(RATE, nullable=False, default=Decimal("1.0"))
    net_inflow: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    inflow_cap_applies: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("ix_lcr_inflow_result_id", "lcr_result_id"),
        Index("ix_lcr_inflow_category", "inflow_category"),
    )
