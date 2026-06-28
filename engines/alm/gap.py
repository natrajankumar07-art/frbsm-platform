"""
Liquidity Gap Engine — ALM repricing/maturity gap analysis.

Takes the bucketed cashflow output from the Cashflow Engine and computes:
  - Liquidity gap per bucket = inflows − outflows
  - Cumulative gap = rolling sum of per-bucket gaps
  - Gap ratio = cumulative gap / total_assets × 100  (regulatory monitoring metric)

A negative cumulative gap signals potential structural funding shortfall.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from engines.alm.cashflow import BucketSummary, CashflowResult
from engines.common.audit import EngineResult, build_trace
from engines.common.utils import canonical_hash, quantize, safe_divide

VERSION = "1.0.0"

_FORMULA_REFS = [
    "ALM — Maturity/repricing gap: inflows minus outflows per time bucket",
    "RBI DSB-II — Cumulative liquidity gap as % of total assets",
]


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class GapBucket(BaseModel):
    """Per-time-bucket gap metrics."""
    time_bucket: str
    bucket_order: int
    inflows: Decimal
    outflows: Decimal
    gap: Decimal          # inflows − outflows
    cumulative_gap: Decimal
    gap_ratio_pct: Decimal  # cumulative_gap / total_assets × 100


class LiquidityGapResult(BaseModel):
    """Complete liquidity gap analysis output."""
    buckets: list[GapBucket]
    total_inflows: Decimal
    total_outflows: Decimal
    net_gap: Decimal
    total_assets_used: Decimal
    currency: str


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def compute_liquidity_gap(
    cashflow_result: CashflowResult,
    total_assets: Decimal,
) -> EngineResult[LiquidityGapResult]:
    """
    Compute per-bucket and cumulative liquidity gaps.

    Args:
        cashflow_result: Output from compute_cashflow_buckets.
        total_assets: Total balance sheet assets (denominator for gap ratio).
    """
    inputs_hash = canonical_hash({
        "cashflow_result": cashflow_result.model_dump(mode="json"),
        "total_assets": str(total_assets),
    })

    gap_buckets: list[GapBucket] = []
    cumulative = Decimal("0")

    for b in cashflow_result.buckets:
        gap = quantize(b.inflows - b.outflows)
        cumulative = quantize(cumulative + gap)
        ratio = quantize(safe_divide(cumulative, total_assets) * Decimal("100"))
        gap_buckets.append(GapBucket(
            time_bucket=b.time_bucket,
            bucket_order=b.bucket_order,
            inflows=b.inflows,
            outflows=b.outflows,
            gap=gap,
            cumulative_gap=cumulative,
            gap_ratio_pct=ratio,
        ))

    result = LiquidityGapResult(
        buckets=gap_buckets,
        total_inflows=cashflow_result.total_inflows,
        total_outflows=cashflow_result.total_outflows,
        net_gap=quantize(cashflow_result.total_inflows - cashflow_result.total_outflows),
        total_assets_used=total_assets,
        currency=cashflow_result.currency,
    )

    outputs_hash = canonical_hash(result.model_dump(mode="json"))
    trace = build_trace(
        engine="liquidity_gap",
        version=VERSION,
        function="compute_liquidity_gap",
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        formula_refs=_FORMULA_REFS,
    )
    return EngineResult(result=result, trace=trace)
