"""Reference data domain models — regulatory parameters, curves, and classification tables."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from .enums import (
    AssetClass,
    CollateralType,
    CurrencyCode,
    CustomerSegment,
    DepositType,
    HQLALevel,
    Jurisdiction,
    RatingGrade,
)


class RiskWeight(BaseModel):
    """
    Basel III Standardised Approach risk weight for a given asset class / rating combination.

    Reference: BCBS CRE20 (credit risk SA), CRE40 (market risk SA).
    Risk weights are expressed as decimals: 1.00 = 100%, 1.50 = 150%.
    """

    model_config = {"frozen": True}

    asset_class: AssetClass
    rating: RatingGrade | None = None  # None = applies to all ratings / unrated
    jurisdiction: Jurisdiction | None = None  # None = global default
    risk_weight: Decimal = Field(..., ge=Decimal("0"), le=Decimal("15"))
    effective_from: date
    regulatory_reference: str  # e.g., "BCBS CRE20.40"


class HQLAHaircut(BaseModel):
    """
    Haircut applied to a collateral type for HQLA eligibility purposes.

    Reference: BCBS LCR30.
    """

    model_config = {"frozen": True}

    hqla_level: HQLALevel
    collateral_type: CollateralType | None = None  # None = applies to level regardless of type
    haircut: Decimal = Field(..., ge=Decimal("0"), le=Decimal("1"))
    effective_from: date
    regulatory_reference: str


class RunOffRate(BaseModel):
    """
    LCR cash outflow run-off rate for a deposit type / customer segment combination.

    Reference: BCBS LCR40.
    """

    model_config = {"frozen": True}

    deposit_type: DepositType
    customer_segment: CustomerSegment
    run_off_rate: Decimal = Field(..., ge=Decimal("0"), le=Decimal("1"))
    effective_from: date
    regulatory_reference: str


class CreditConversionFactor(BaseModel):
    """
    CCF converts off-balance-sheet commitments to credit equivalent exposures.

    Reference: BCBS CRE20.94.
    """

    model_config = {"frozen": True}

    commitment_type: str = Field(..., max_length=100)
    original_maturity_lt_1y: bool | None = None  # None = maturity-independent
    ccf: Decimal = Field(..., ge=Decimal("0"), le=Decimal("1"))
    effective_from: date
    regulatory_reference: str


class YieldCurve(BaseModel):
    """
    A point-in-time yield curve used for discounting, EVE, and NII calculations.

    Rates are annualised decimals: 0.05 = 5% per annum.
    Tenors are in years.
    """

    model_config = {"frozen": True}

    currency: CurrencyCode
    curve_type: str = Field(
        ..., pattern=r"^(zero|swap|basis|ois|repo|government)$"
    )
    tenors_years: tuple[Decimal, ...] = Field(..., min_length=2)
    rates: tuple[Decimal, ...]
    as_of_date: date

    @property
    def is_inverted(self) -> bool:
        """True if short-end rate exceeds long-end rate (yield curve inversion)."""
        return self.rates[-1] < self.rates[0]
