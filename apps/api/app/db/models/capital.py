"""Capital adequacy result ORM models — CET1, Tier 1, Total Capital, RWA, ratios."""

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

MONEY = Numeric(precision=28, scale=8)
RATE = Numeric(precision=10, scale=6)


class CapitalResultModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Basel III capital adequacy computation result for a snapshot/entity pair."""

    __tablename__ = "capital_results"

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
    # Capital components
    cet1_capital: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    additional_tier1: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    tier2_capital: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    total_capital: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    # RWA by risk type
    rwa_credit: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    rwa_market: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    rwa_operational: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    total_rwa: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    # Capital ratios
    cet1_ratio: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    tier1_ratio: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    total_capital_ratio: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    leverage_ratio: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    # Regulatory thresholds (from entity_capital_requirements at snapshot date)
    cet1_minimum: Mapped[Decimal] = mapped_column(RATE, nullable=False, default=Decimal("0.045"))
    tier1_minimum: Mapped[Decimal] = mapped_column(RATE, nullable=False, default=Decimal("0.06"))
    total_minimum: Mapped[Decimal] = mapped_column(RATE, nullable=False, default=Decimal("0.08"))
    passes_all: Mapped[bool] = mapped_column(Boolean, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    __table_args__ = (
        UniqueConstraint("snapshot_id", "entity_id", name="uq_capital_snapshot_entity"),
        Index("ix_capital_snapshot_entity", "snapshot_id", "entity_id"),
        Index("ix_capital_compute_run", "compute_run_id"),
        Index("ix_capital_passes_all", "passes_all"),
    )
