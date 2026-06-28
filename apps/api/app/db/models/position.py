"""Position and Collateral ORM models."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Date,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, TimestampMixin

MONEY = Numeric(precision=28, scale=8)


class PositionModel(TimestampMixin, Base):
    """
    ORM model for the range-partitioned `positions` table.

    The partition key (reporting_date) is part of the composite PRIMARY KEY
    (id, reporting_date) as required by PostgreSQL partitioned tables.
    UUIDPrimaryKeyMixin is intentionally NOT used here — it declares only `id`
    as PK, which would misrepresent the composite key to SQLAlchemy's identity map.
    """

    __tablename__ = "positions"

    # Composite PK required by PostgreSQL range partitioning
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    reporting_date: Mapped[date] = mapped_column(Date, nullable=False, primary_key=True)

    counterparty_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    product_code: Mapped[str] = mapped_column(String(50), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    notional: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    booked_amount: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    fair_value: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    accrued_interest: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    maturity_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    repricing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    behavioural_maturity: Mapped[date | None] = mapped_column(Date, nullable=True)
    asset_class: Mapped[str] = mapped_column(String(50), nullable=False)
    credit_grade: Mapped[str] = mapped_column(String(10), nullable=False, default="UNRATED")
    ifrs9_stage: Mapped[str] = mapped_column(String(10), nullable=False, default="stage_1")
    days_past_due: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hqla_level: Mapped[str] = mapped_column(String(20), nullable=False, default="ineligible")
    deposit_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    customer_segment: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    counterparty: Mapped["CounterpartyModel"] = relationship(  # type: ignore[name-defined]
        "CounterpartyModel",
        back_populates="positions",
        foreign_keys=[counterparty_id],
        lazy="joined",
    )
    collateral: Mapped[list["CollateralModel"]] = relationship(
        "CollateralModel",
        back_populates="position",
        primaryjoin=(
            "and_(PositionModel.id == CollateralModel.position_id, "
            "PositionModel.reporting_date == CollateralModel.position_reporting_date)"
        ),
        foreign_keys="[CollateralModel.position_id, CollateralModel.position_reporting_date]",
        lazy="selectin",
    )

    __table_args__ = (
        # Enforce counterparty FK at DB level (declared here to support partitioned table)
        ForeignKeyConstraint(
            ["counterparty_id"],
            ["counterparties.id"],
            ondelete="RESTRICT",
            name="fk_positions_counterparty",
        ),
        Index("ix_positions_counterparty_id", "counterparty_id"),
        Index("ix_positions_reporting_date", "reporting_date"),
        Index("ix_positions_ifrs9_stage", "ifrs9_stage"),
        Index("ix_positions_asset_class", "asset_class"),
        Index("ix_positions_status", "status"),
    )


class CollateralModel(TimestampMixin, Base):
    """
    ORM model for the `collateral` table.

    Uses a composite FK (position_id, position_reporting_date) to reference
    the partitioned positions table — PostgreSQL requires the partition key
    in any FK targeting a partitioned table.
    """

    __tablename__ = "collateral"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    position_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    position_reporting_date: Mapped[date] = mapped_column(Date, nullable=False)
    collateral_type: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    market_value: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    haircut: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    net_value: Mapped[Decimal] = mapped_column(MONEY, nullable=False)

    position: Mapped["PositionModel"] = relationship(
        "PositionModel",
        back_populates="collateral",
        foreign_keys=[position_id, position_reporting_date],
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["position_id", "position_reporting_date"],
            ["positions.id", "positions.reporting_date"],
            ondelete="CASCADE",
            name="collateral_position_fkey",
        ),
        Index("ix_collateral_position_id", "position_id"),
    )
