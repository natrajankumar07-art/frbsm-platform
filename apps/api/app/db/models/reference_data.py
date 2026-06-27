"""Reference data ORM models — risk weights, haircuts, run-off rates, CCFs, curves."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Index, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

RATE = Numeric(precision=10, scale=6)  # rates, haircuts, weights (0.000000 to 9999.999999)


class RiskWeightModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reference_risk_weights"

    asset_class: Mapped[str] = mapped_column(String(50), nullable=False)
    rating: Mapped[str | None] = mapped_column(String(10), nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(10), nullable=True)
    risk_weight: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    regulatory_reference: Mapped[str] = mapped_column(String(200), nullable=False)

    __table_args__ = (
        Index("ix_rw_asset_class_rating", "asset_class", "rating"),
        Index("ix_rw_effective_from", "effective_from"),
    )


class HQLAHaircutModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reference_hqla_haircuts"

    hqla_level: Mapped[str] = mapped_column(String(20), nullable=False)
    collateral_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    haircut: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    regulatory_reference: Mapped[str] = mapped_column(String(200), nullable=False)

    __table_args__ = (Index("ix_hqla_level_effective", "hqla_level", "effective_from"),)


class RunOffRateModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reference_run_off_rates"

    deposit_type: Mapped[str] = mapped_column(String(60), nullable=False)
    customer_segment: Mapped[str] = mapped_column(String(30), nullable=False)
    run_off_rate: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    regulatory_reference: Mapped[str] = mapped_column(String(200), nullable=False)

    __table_args__ = (
        Index("ix_run_off_deposit_segment", "deposit_type", "customer_segment"),
    )


class CreditConversionFactorModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reference_ccf"

    commitment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    original_maturity_lt_1y: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ccf: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    regulatory_reference: Mapped[str] = mapped_column(String(200), nullable=False)


class YieldCurveModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reference_yield_curves"

    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    curve_type: Mapped[str] = mapped_column(String(20), nullable=False)
    tenors_years: Mapped[list[float]] = mapped_column(ARRAY(Numeric(10, 4)), nullable=False)
    rates: Mapped[list[float]] = mapped_column(ARRAY(Numeric(10, 6)), nullable=False)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        Index("ix_yield_curve_ccy_type_date", "currency", "curve_type", "as_of_date"),
    )
