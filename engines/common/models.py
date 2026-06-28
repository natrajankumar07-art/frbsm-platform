"""Engine-specific input/output models shared across engines.

These complement the canonical domain models in `shared/domain/domain/`.
Where an engine needs a simplified or engine-specific view, define it here.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# LCR inputs
# ---------------------------------------------------------------------------

class HQLAPosition(BaseModel):
    """A single HQLA-eligible (or ineligible) position for LCR computation."""

    model_config = {"frozen": True}

    hqla_level: Literal["level_1", "level_2a", "level_2b", "ineligible"]
    asset_class: str
    gross_amount: Decimal = Field(..., ge=Decimal("0"))
    haircut_override: Decimal | None = None  # overrides standard haircut table


class OutflowItem(BaseModel):
    """A single cash outflow category for LCR computation (LCR40)."""

    model_config = {"frozen": True}

    category: str
    deposit_type: str | None = None
    customer_segment: str | None = None
    balance: Decimal = Field(..., ge=Decimal("0"))
    run_off_rate: Decimal = Field(..., ge=Decimal("0"), le=Decimal("1"))


class InflowItem(BaseModel):
    """A single contractual inflow for LCR computation (LCR40)."""

    model_config = {"frozen": True}

    category: str
    asset_class: str | None = None
    amount: Decimal = Field(..., ge=Decimal("0"))
    inflow_rate: Decimal = Field(default=Decimal("1"), ge=Decimal("0"), le=Decimal("1"))
    exclude_from_inflows: bool = False  # True if asset already counted in HQLA stock


class LCRInput(BaseModel):
    """Complete input set for a single LCR computation."""

    model_config = {"frozen": True}

    snapshot_id: str
    entity_id: str
    reporting_date: date
    hqla_positions: list[HQLAPosition]
    outflow_items: list[OutflowItem]
    inflow_items: list[InflowItem]
    currency: str = "INR"
    minimum_ratio: Decimal = Decimal("1.0")


# ---------------------------------------------------------------------------
# NSFR inputs
# ---------------------------------------------------------------------------

class NSFRFundingItem(BaseModel):
    """An ASF funding source item for NSFR computation (NSF20)."""

    model_config = {"frozen": True}

    category: str
    balance: Decimal = Field(..., ge=Decimal("0"))
    asf_factor: Decimal = Field(..., ge=Decimal("0"), le=Decimal("1"))
    maturity_bucket: str  # lt_6m | 6m_1y | gt_1y | overnight | perpetual


class NSFRAssetItem(BaseModel):
    """An RSF asset item for NSFR computation (NSF20)."""

    model_config = {"frozen": True}

    category: str
    balance: Decimal = Field(..., ge=Decimal("0"))
    rsf_factor: Decimal = Field(..., ge=Decimal("0"), le=Decimal("1"))
    maturity_bucket: str  # lt_6m | 6m_1y | gt_1y | any


class NSFRInput(BaseModel):
    """Complete input set for a single NSFR computation."""

    model_config = {"frozen": True}

    snapshot_id: str
    entity_id: str
    reporting_date: date
    funding_items: list[NSFRFundingItem]  # ASF sources
    asset_items: list[NSFRAssetItem]       # RSF uses
    currency: str = "INR"
    minimum_ratio: Decimal = Decimal("1.0")


# ---------------------------------------------------------------------------
# Capital inputs
# ---------------------------------------------------------------------------

class RWAPositionItem(BaseModel):
    """A single position item for credit RWA computation (CRE20)."""

    model_config = {"frozen": True}

    position_id: str
    asset_class: str
    credit_grade: str
    jurisdiction: str | None = None
    booked_amount: Decimal = Field(..., ge=Decimal("0"))
    risk_weight: Decimal = Field(..., ge=Decimal("0"))  # resolved from reference table


class CapitalInput(BaseModel):
    """Complete input set for capital adequacy computation."""

    model_config = {"frozen": True}

    snapshot_id: str
    entity_id: str
    reporting_date: date
    rwa_positions: list[RWAPositionItem]
    rwa_market: Decimal = Decimal("0")         # market risk RWA (SA)
    rwa_operational: Decimal = Decimal("0")    # op risk RWA (BIA / SA-OR)
    cet1_capital: Decimal = Field(..., ge=Decimal("0"))
    additional_tier1: Decimal = Decimal("0")
    tier2_capital: Decimal = Decimal("0")
    total_exposure: Decimal = Field(..., ge=Decimal("0"))  # leverage ratio denominator
    cet1_minimum: Decimal = Decimal("0.045")
    tier1_minimum: Decimal = Decimal("0.060")
    total_minimum: Decimal = Decimal("0.080")
    leverage_minimum: Decimal = Decimal("0.030")
    currency: str = "INR"


# ---------------------------------------------------------------------------
# Balance sheet inputs
# ---------------------------------------------------------------------------

class BSPositionItem(BaseModel):
    """Simplified position view for balance sheet aggregation."""

    model_config = {"frozen": True}

    position_id: str
    asset_class: str
    deposit_type: str | None = None  # non-None → liability
    booked_amount: Decimal
    currency: str


class BalanceSheetInput(BaseModel):
    """Complete input set for balance sheet computation."""

    model_config = {"frozen": True}

    snapshot_id: str
    entity_id: str
    reporting_date: date
    positions: list[BSPositionItem]
    total_equity: Decimal | None = None  # if None, derived as assets − liabilities
    off_balance_sheet_items: Decimal = Decimal("0")
    currency: str = "INR"


# ---------------------------------------------------------------------------
# Cashflow / SLS inputs
# ---------------------------------------------------------------------------

class CashflowItem(BaseModel):
    """A single projected cashflow for ALM bucketing."""

    model_config = {"frozen": True}

    cashflow_id: str
    position_id: str
    cashflow_type: str  # principal | interest | fee
    cashflow_date: date
    amount: Decimal  # positive = inflow (asset matures), negative = outflow (liability matures)
    currency: str


class CashflowInput(BaseModel):
    """Complete cashflow dataset for a reporting period."""

    model_config = {"frozen": True}

    snapshot_id: str
    entity_id: str
    reporting_date: date
    cashflows: list[CashflowItem]
    currency: str = "INR"


# ---------------------------------------------------------------------------
# Stress test inputs
# ---------------------------------------------------------------------------

class ScenarioParameter(BaseModel):
    """A single shock parameter in a stress scenario."""

    model_config = {"frozen": True}

    parameter_type: str  # credit | liquidity | capital | rate
    parameter_name: str  # pd_shock | lgd_shock | rwa_shock | outflow_shock | hqla_shock | parallel_shift
    shock_type: Literal["absolute", "relative", "replace"]
    shock_value: Decimal


class StressTestInput(BaseModel):
    """Complete input for a stress test run."""

    model_config = {"frozen": True}

    scenario_code: str
    snapshot_id: str
    entity_id: str
    reporting_date: date
    baseline_lcr_input: LCRInput | None = None
    baseline_nsfr_input: NSFRInput | None = None
    baseline_capital_input: CapitalInput | None = None
    parameters: list[ScenarioParameter]
    currency: str = "INR"
