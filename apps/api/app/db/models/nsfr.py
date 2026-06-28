"""NSFR (Net Stable Funding Ratio) result ORM models per Basel III NSFR standard."""

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

MONEY = Numeric(precision=28, scale=8)
RATE = Numeric(precision=10, scale=6)


class NSFRResultModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Top-level NSFR computation result for a snapshot/entity pair."""

    __tablename__ = "nsfr_results"

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
    available_stable_funding: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    required_stable_funding: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    nsfr_ratio: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    minimum_ratio: Mapped[Decimal] = mapped_column(RATE, nullable=False, default=Decimal("1.0"))
    passes: Mapped[bool] = mapped_column(Boolean, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    __table_args__ = (
        UniqueConstraint("snapshot_id", "entity_id", name="uq_nsfr_snapshot_entity"),
        Index("ix_nsfr_snapshot_entity", "snapshot_id", "entity_id"),
        Index("ix_nsfr_compute_run", "compute_run_id"),
        Index("ix_nsfr_passes", "passes"),
    )


class NSFRASFComponentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Available Stable Funding (ASF) breakdown for a NSFR result."""

    __tablename__ = "nsfr_asf_components"

    nsfr_result_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("nsfr_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    funding_category: Mapped[str] = mapped_column(String(100), nullable=False)
    remaining_maturity_bucket: Mapped[str] = mapped_column(String(30), nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    asf_factor: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    weighted_amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False)

    __table_args__ = (
        Index("ix_nsfr_asf_result_id", "nsfr_result_id"),
        Index("ix_nsfr_asf_category", "funding_category"),
    )


class NSFRRSFComponentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Required Stable Funding (RSF) breakdown for a NSFR result."""

    __tablename__ = "nsfr_rsf_components"

    nsfr_result_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("nsfr_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    asset_category: Mapped[str] = mapped_column(String(100), nullable=False)
    remaining_maturity_bucket: Mapped[str] = mapped_column(String(30), nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    rsf_factor: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    weighted_amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False)

    __table_args__ = (
        Index("ix_nsfr_rsf_result_id", "nsfr_result_id"),
        Index("ix_nsfr_rsf_category", "asset_category"),
    )
