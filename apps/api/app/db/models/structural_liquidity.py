"""
Structural Liquidity Statement (SLS) ORM models.

The Structural Liquidity Statement is an RBI regulatory return (DSB-II format)
that shows the maturity profile of a bank's assets and liabilities across
standardised time buckets, and the resulting liquidity gap/surplus.
"""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

MONEY = Numeric(precision=28, scale=8)


class StructuralLiquidityBucketModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Aggregated inflows/outflows and net position per RBI SLS time bucket.

    Time buckets follow RBI DSB-II format:
      0_1d, 1_7d, 7_14d, 14_28d, 28d_3m, 3m_6m, 6m_1y, 1y_3y, 3y_5y, gt_5y
    """

    __tablename__ = "structural_liquidity_buckets"

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
    time_bucket: Mapped[str] = mapped_column(String(20), nullable=False)
    bucket_order: Mapped[int] = mapped_column(Integer, nullable=False)
    total_inflows: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    total_outflows: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    net_position: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    cumulative_net: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    __table_args__ = (
        UniqueConstraint(
            "snapshot_id", "entity_id", "time_bucket",
            name="uq_slb_snapshot_entity_bucket",
        ),
        Index("ix_slb_snapshot_entity", "snapshot_id", "entity_id"),
        Index("ix_slb_time_bucket", "time_bucket"),
        Index("ix_slb_bucket_order", "bucket_order"),
    )
