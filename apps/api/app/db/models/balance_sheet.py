"""Balance sheet ORM models — line items and summary per snapshot."""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

MONEY = Numeric(precision=28, scale=8)


class BalanceSheetLineItemModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Individual account-level balance sheet entry for a snapshot/entity."""

    __tablename__ = "balance_sheet_line_items"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("snapshots.id", ondelete="RESTRICT"),
        nullable=False,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    account_code: Mapped[str] = mapped_column(String(50), nullable=False)
    account_name: Mapped[str] = mapped_column(String(200), nullable=False)
    line_item_type: Mapped[str] = mapped_column(String(30), nullable=False)
    product_group_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount_local: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    amount_reporting: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    reporting_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        Index("ix_bsli_snapshot_entity", "snapshot_id", "entity_id"),
        Index("ix_bsli_account_code", "account_code"),
        Index("ix_bsli_line_item_type", "line_item_type"),
        Index("ix_bsli_product_group", "product_group_id"),
    )


class BalanceSheetSummaryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Aggregated balance sheet totals for a snapshot/entity — produced by a compute run."""

    __tablename__ = "balance_sheet_summaries"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("snapshots.id", ondelete="RESTRICT"),
        nullable=False,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    total_assets: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    total_liabilities: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    total_equity: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    total_off_balance_sheet: Mapped[Decimal] = mapped_column(
        MONEY, nullable=False, default=Decimal("0")
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    compute_run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("compute_runs.id", ondelete="RESTRICT"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("snapshot_id", "entity_id", name="uq_bs_summary_snapshot_entity"),
        Index("ix_bss_snapshot_entity", "snapshot_id", "entity_id"),
        Index("ix_bss_compute_run", "compute_run_id"),
    )
