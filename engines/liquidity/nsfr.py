"""
NSFR (Net Stable Funding Ratio) Engine — Basel III NSFR standard.

Reference: BCBS "Basel III: the net stable funding ratio" (October 2014),
NSF20 (ASF factors) and NSF30 (RSF factors).

Formula:
    NSFR = Available Stable Funding (ASF) / Required Stable Funding (RSF) ≥ 100%
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from engines.common.audit import EngineResult, build_trace
from engines.common.models import NSFRAssetItem, NSFRFundingItem, NSFRInput
from engines.common.utils import canonical_hash, quantize, safe_divide

VERSION = "1.0.0"

_FORMULA_REFS = [
    "BCBS NSF20 — Available Stable Funding factors",
    "BCBS NSF30 — Required Stable Funding factors",
    "BCBS NSF10 — NSFR = ASF / RSF ≥ 100%",
]


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class ASFComponent(BaseModel):
    """One Available Stable Funding source."""
    category: str
    maturity_bucket: str
    gross_amount: Decimal
    asf_factor: Decimal
    weighted_amount: Decimal


class RSFComponent(BaseModel):
    """One Required Stable Funding use."""
    category: str
    maturity_bucket: str
    gross_amount: Decimal
    rsf_factor: Decimal
    weighted_amount: Decimal


class NSFRResult(BaseModel):
    """Complete NSFR computation output."""
    available_stable_funding: Decimal
    required_stable_funding: Decimal
    nsfr_ratio: Decimal
    minimum_ratio: Decimal
    passes: bool
    currency: str
    asf_components: list[ASFComponent]
    rsf_components: list[RSFComponent]


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def compute_nsfr(inputs: NSFRInput) -> EngineResult[NSFRResult]:
    """
    Compute the Basel III Net Stable Funding Ratio.

    Inputs are pre-classified funding/asset items with their ASF/RSF factors
    applied by the data preparation layer (derived from the reference tables).
    """
    inputs_hash = canonical_hash(inputs.model_dump(mode="json"))

    # ── ASF: sum of weighted funding sources ─────────────────────────────────
    asf_total = Decimal("0")
    asf_components: list[ASFComponent] = []
    for item in inputs.funding_items:
        weighted = quantize(item.balance * item.asf_factor)
        asf_total += weighted
        asf_components.append(ASFComponent(
            category=item.category,
            maturity_bucket=item.maturity_bucket,
            gross_amount=item.balance,
            asf_factor=item.asf_factor,
            weighted_amount=weighted,
        ))
    asf_total = quantize(asf_total)

    # ── RSF: sum of weighted asset uses ──────────────────────────────────────
    rsf_total = Decimal("0")
    rsf_components: list[RSFComponent] = []
    for item in inputs.asset_items:
        weighted = quantize(item.balance * item.rsf_factor)
        rsf_total += weighted
        rsf_components.append(RSFComponent(
            category=item.category,
            maturity_bucket=item.maturity_bucket,
            gross_amount=item.balance,
            rsf_factor=item.rsf_factor,
            weighted_amount=weighted,
        ))
    rsf_total = quantize(rsf_total)

    # ── NSFR ratio ────────────────────────────────────────────────────────────
    nsfr_ratio = quantize(safe_divide(asf_total, rsf_total))
    passes = nsfr_ratio >= inputs.minimum_ratio

    result = NSFRResult(
        available_stable_funding=asf_total,
        required_stable_funding=rsf_total,
        nsfr_ratio=nsfr_ratio,
        minimum_ratio=inputs.minimum_ratio,
        passes=passes,
        currency=inputs.currency,
        asf_components=asf_components,
        rsf_components=rsf_components,
    )

    outputs_hash = canonical_hash(result.model_dump(mode="json"))
    trace = build_trace(
        engine="nsfr",
        version=VERSION,
        function="compute_nsfr",
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        formula_refs=_FORMULA_REFS,
    )
    return EngineResult(result=result, trace=trace)
