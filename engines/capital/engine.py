"""
Capital Adequacy Engine — Basel III capital ratios.

Reference: BCBS CRE20 (Standardised Approach credit risk), CAP10 (capital
ratios), and RBI Master Circular — Basel III Capital Regulations (2023).

Formulas:
    CET1 ratio          = CET1 capital / Total RWA
    Tier 1 ratio        = (CET1 + AT1) / Total RWA
    Total Capital ratio = (CET1 + AT1 + T2) / Total RWA
    Leverage ratio      = Tier 1 capital / Total Exposure
    Total RWA           = Credit RWA + Market RWA + Operational RWA
    Credit RWA          = Σ (booked_amount × risk_weight) for each position
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from engines.common.audit import EngineResult, build_trace
from engines.common.models import CapitalInput, RWAPositionItem
from engines.common.utils import canonical_hash, quantize, safe_divide

VERSION = "1.0.0"

_FORMULA_REFS = [
    "BCBS CRE20 — Standardised Approach: credit risk weights",
    "BCBS CAP10 — CET1, Tier 1, Total Capital ratios",
    "BCBS LEV10 — Leverage ratio: T1 / Total Exposure",
    "RBI Master Circular Basel III Capital Regulations 2023",
]


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class RWAComponent(BaseModel):
    """Per-position credit RWA breakdown."""
    position_id: str
    asset_class: str
    credit_grade: str
    booked_amount: Decimal
    risk_weight: Decimal
    risk_weighted_amount: Decimal


class CapitalResult(BaseModel):
    """Complete capital adequacy computation output."""
    # Capital components
    cet1_capital: Decimal
    additional_tier1: Decimal
    tier1_capital: Decimal
    tier2_capital: Decimal
    total_capital: Decimal
    # RWA
    rwa_credit: Decimal
    rwa_market: Decimal
    rwa_operational: Decimal
    total_rwa: Decimal
    # Ratios
    cet1_ratio: Decimal
    tier1_ratio: Decimal
    total_capital_ratio: Decimal
    leverage_ratio: Decimal
    # Thresholds
    cet1_minimum: Decimal
    tier1_minimum: Decimal
    total_minimum: Decimal
    leverage_minimum: Decimal
    passes_cet1: bool
    passes_tier1: bool
    passes_total: bool
    passes_leverage: bool
    passes_all: bool
    currency: str
    # Breakdown
    rwa_components: list[RWAComponent]


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def compute_capital(inputs: CapitalInput) -> EngineResult[CapitalResult]:
    """
    Compute Basel III capital adequacy ratios.

    Risk weights are pre-resolved from the reference table by the caller
    (each RWAPositionItem carries its risk_weight as a Decimal fraction).
    """
    inputs_hash = canonical_hash(inputs.model_dump(mode="json"))

    # ── Credit RWA ────────────────────────────────────────────────────────────
    rwa_credit = Decimal("0")
    rwa_components: list[RWAComponent] = []
    for pos in inputs.rwa_positions:
        rwa = quantize(pos.booked_amount * pos.risk_weight)
        rwa_credit += rwa
        rwa_components.append(RWAComponent(
            position_id=pos.position_id,
            asset_class=pos.asset_class,
            credit_grade=pos.credit_grade,
            booked_amount=pos.booked_amount,
            risk_weight=pos.risk_weight,
            risk_weighted_amount=rwa,
        ))
    rwa_credit = quantize(rwa_credit)

    # ── Total RWA ─────────────────────────────────────────────────────────────
    total_rwa = quantize(rwa_credit + inputs.rwa_market + inputs.rwa_operational)

    # ── Capital tiers ─────────────────────────────────────────────────────────
    tier1 = quantize(inputs.cet1_capital + inputs.additional_tier1)
    total_capital = quantize(tier1 + inputs.tier2_capital)

    # ── Ratios ────────────────────────────────────────────────────────────────
    cet1_ratio = quantize(safe_divide(inputs.cet1_capital, total_rwa))
    tier1_ratio = quantize(safe_divide(tier1, total_rwa))
    total_ratio = quantize(safe_divide(total_capital, total_rwa))
    leverage_ratio = quantize(safe_divide(tier1, inputs.total_exposure))

    passes_cet1 = cet1_ratio >= inputs.cet1_minimum
    passes_tier1 = tier1_ratio >= inputs.tier1_minimum
    passes_total = total_ratio >= inputs.total_minimum
    passes_leverage = leverage_ratio >= inputs.leverage_minimum

    result = CapitalResult(
        cet1_capital=inputs.cet1_capital,
        additional_tier1=inputs.additional_tier1,
        tier1_capital=tier1,
        tier2_capital=inputs.tier2_capital,
        total_capital=total_capital,
        rwa_credit=rwa_credit,
        rwa_market=inputs.rwa_market,
        rwa_operational=inputs.rwa_operational,
        total_rwa=total_rwa,
        cet1_ratio=cet1_ratio,
        tier1_ratio=tier1_ratio,
        total_capital_ratio=total_ratio,
        leverage_ratio=leverage_ratio,
        cet1_minimum=inputs.cet1_minimum,
        tier1_minimum=inputs.tier1_minimum,
        total_minimum=inputs.total_minimum,
        leverage_minimum=inputs.leverage_minimum,
        passes_cet1=passes_cet1,
        passes_tier1=passes_tier1,
        passes_total=passes_total,
        passes_leverage=passes_leverage,
        passes_all=passes_cet1 and passes_tier1 and passes_total and passes_leverage,
        currency=inputs.currency,
        rwa_components=rwa_components,
    )

    outputs_hash = canonical_hash(result.model_dump(mode="json"))
    trace = build_trace(
        engine="capital",
        version=VERSION,
        function="compute_capital",
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        formula_refs=_FORMULA_REFS,
    )
    return EngineResult(result=result, trace=trace)
