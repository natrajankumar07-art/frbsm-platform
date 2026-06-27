"""Position and Collateral ORM models."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

MONEY = Numeric(precision=28, scale=8)


class PositionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "positions"

    counterparty_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("counterparties.id", ondelete="RESTRICT"),
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
    reporting_date: Mapped[date] = mapped_column(Date, nullable=False)

    counterparty: Mapped["CounterpartyModel"] = relationship(  # type: ignore[name-defined]
        "CounterpartyModel",
        back_populates="positions",
        lazy="joined",
    )
    collateral: Mapped[list["CollateralModel"]] = relationship(
        "CollateralModel",
        back_populates="position",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_positions_counterparty_id", "counterparty_id"),
        Index("ix_positions_reporting_date", "reporting_date"),
        Index("ix_positions_ifrs9_stage", "ifrs9_stage"),
        Index("ix_positions_asset_class", "asset_class"),
        Index("ix_positions_status", "status"),
    )


class CollateralModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "collateral"

    position_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("positions.id", ondelete="CASCADE"),
        nullable=False,
    )
    collateral_type: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    market_value: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    haircut: Mapped[Decimal] = mapped_column(MONEY, nullable=False, default=Decimal("0"))
    net_value: Mapped[Decimal] = mapped_column(MONEY, nullable=False)

    position: Mapped["PositionModel"] = relationship(
        "PositionModel",
        back_populates="collateral",
    )

    __table_args__ = (Index("ix_collateral_position_id", "position_id"),)
