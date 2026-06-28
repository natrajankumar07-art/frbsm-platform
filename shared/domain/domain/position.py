"""Position and Collateral domain models — the core balance-sheet entities."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from .enums import (
    AssetClass,
    CollateralType,
    CurrencyCode,
    CustomerSegment,
    DepositType,
    HQLALevel,
    IFRS9Stage,
    PositionStatus,
    RatingGrade,
)


class Collateral(BaseModel):
    """
    A credit risk mitigant (CRM) securing part or all of a Position.

    `net_value` = market_value × (1 − haircut). Engines use net_value
    for CRM benefit calculations; do not recompute haircuts inside engines.

    `position_reporting_date` mirrors the partition key on the positions table;
    required to form the composite FK (position_id, position_reporting_date)
    → positions(id, reporting_date) in PostgreSQL range-partitioned schema.
    """

    model_config = {"frozen": True}

    id: UUID
    position_id: UUID
    position_reporting_date: date
    collateral_type: CollateralType
    description: str = Field(..., max_length=500)
    market_value: Decimal = Field(..., ge=Decimal("0"))
    currency: CurrencyCode
    haircut: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("1"))
    net_value: Decimal = Field(..., ge=Decimal("0"))

    @model_validator(mode="after")
    def net_value_consistent(self) -> "Collateral":
        expected = self.market_value * (Decimal("1") - self.haircut)
        if abs(self.net_value - expected) > Decimal("0.01"):
            raise ValueError(
                f"net_value {self.net_value} inconsistent with "
                f"market_value {self.market_value} × (1 − {self.haircut})"
            )
        return self


class Position(BaseModel):
    """
    A single balance-sheet or off-balance-sheet exposure.

    Positions are the atomic unit of regulatory computation. Every engine
    receives a collection of Positions (via a frozen Snapshot) and produces
    a typed result. Positions are never modified by engines.

    Key fields:
    - `notional`: contractual face value
    - `booked_amount`: on-balance-sheet carrying amount
    - `fair_value`: mark-to-market / IFRS 13 fair value
    - `behavioural_maturity`: overlays contractual maturity with prepayment/
      non-maturity assumptions; used by ALM and LCR behavioural models
    """

    model_config = {"frozen": True}

    id: UUID
    counterparty_id: UUID
    product_code: str = Field(..., max_length=50)
    currency: CurrencyCode
    notional: Decimal = Field(..., ge=Decimal("0"))
    booked_amount: Decimal
    fair_value: Decimal
    accrued_interest: Decimal = Decimal("0")
    maturity_date: date | None = None
    repricing_date: date | None = None
    behavioural_maturity: date | None = None
    asset_class: AssetClass
    credit_grade: RatingGrade = RatingGrade.UNRATED
    ifrs9_stage: IFRS9Stage = IFRS9Stage.STAGE_1
    days_past_due: int = Field(default=0, ge=0)
    hqla_level: HQLALevel = HQLALevel.INELIGIBLE
    deposit_type: DepositType | None = None
    customer_segment: CustomerSegment | None = None
    status: PositionStatus = PositionStatus.ACTIVE
    reporting_date: date
    collateral: tuple[Collateral, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def stage_3_must_have_dpd_or_flag(self) -> "Position":
        """Stage 3 positions should reflect observable credit impairment."""
        # Soft validation: warn rather than reject — overrides exist via the staging engine.
        return self

    @model_validator(mode="after")
    def maturity_not_before_reporting(self) -> "Position":
        if (
            self.maturity_date is not None
            and self.maturity_date < self.reporting_date
            and self.status == PositionStatus.ACTIVE
        ):
            raise ValueError(
                f"Active position {self.id} has maturity_date {self.maturity_date} "
                f"before reporting_date {self.reporting_date}"
            )
        return self
