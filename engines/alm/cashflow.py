"""
Cashflow Engine — ALM cashflow bucketing.

Buckets projected cashflows into 10 RBI DSB-II time bands based on the
number of days from the reporting date to each cashflow date.

This engine is a pre-processor for the SLS engine and the Liquidity Gap
engine. It consumes raw cashflow schedules and returns per-bucket totals.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from engines.common.audit import EngineResult, build_trace
from engines.common.models import CashflowInput
from engines.common.utils import canonical_hash, quantize

VERSION = "1.0.0"

_FORMULA_REFS = [
    "RBI DSB-II — Structural Liquidity Statement time buckets",
    "ALM standard: cashflow maturity profiling",
]

# (name, min_days_exclusive, max_days_inclusive)
_BUCKETS: list[tuple[str, int, int]] = [
    ("0_1d",    0,    1),
    ("1_7d",    1,    7),
    ("7_14d",   7,   14),
    ("14_28d",  14,  28),
    ("28d_3m",  28,  92),
    ("3m_6m",   92, 183),
    ("6m_1y",  183, 365),
    ("1y_3y",  365, 1095),
    ("3y_5y", 1095, 1826),
    ("gt_5y", 1826, 999_999),
]

_BUCKET_ORDER = {name: i + 1 for i, (name, _, _) in enumerate(_BUCKETS)}


def _assign_bucket(days: int) -> str:
    for name, lo, hi in _BUCKETS:
        if lo < days <= hi:
            return name
    return "gt_5y"


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class BucketSummary(BaseModel):
    """Per-time-bucket cashflow aggregation."""
    time_bucket: str
    bucket_order: int
    inflows: Decimal   # maturing assets, interest received
    outflows: Decimal  # maturing liabilities, interest paid
    net: Decimal
    cumulative_net: Decimal


class CashflowResult(BaseModel):
    """Bucketed cashflow summary across all time bands."""
    buckets: list[BucketSummary]
    total_inflows: Decimal
    total_outflows: Decimal
    reporting_date: date
    currency: str


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def compute_cashflow_buckets(inputs: CashflowInput) -> EngineResult[CashflowResult]:
    """
    Assign each cashflow to a time bucket and aggregate.

    Convention:
      amount > 0 → inflow  (asset principal/interest maturing)
      amount < 0 → outflow (liability principal/interest due)

    Cashflows on or before the reporting_date are placed in bucket "0_1d"
    (treated as due today / overdue).
    """
    inputs_hash = canonical_hash(inputs.model_dump(mode="json"))

    inflows: dict[str, Decimal] = {b[0]: Decimal("0") for b in _BUCKETS}
    outflows: dict[str, Decimal] = {b[0]: Decimal("0") for b in _BUCKETS}

    for cf in inputs.cashflows:
        days = max(0, (cf.cashflow_date - inputs.reporting_date).days)
        bucket = "0_1d" if days == 0 else _assign_bucket(days)
        if cf.amount >= Decimal("0"):
            inflows[bucket] += cf.amount
        else:
            outflows[bucket] += abs(cf.amount)

    result_buckets: list[BucketSummary] = []
    cumulative = Decimal("0")
    grand_in = Decimal("0")
    grand_out = Decimal("0")

    for name, _, _ in _BUCKETS:
        b_in = quantize(inflows[name])
        b_out = quantize(outflows[name])
        net = quantize(b_in - b_out)
        cumulative = quantize(cumulative + net)
        grand_in += b_in
        grand_out += b_out
        result_buckets.append(BucketSummary(
            time_bucket=name,
            bucket_order=_BUCKET_ORDER[name],
            inflows=b_in,
            outflows=b_out,
            net=net,
            cumulative_net=cumulative,
        ))

    result = CashflowResult(
        buckets=result_buckets,
        total_inflows=quantize(grand_in),
        total_outflows=quantize(grand_out),
        reporting_date=inputs.reporting_date,
        currency=inputs.currency,
    )

    outputs_hash = canonical_hash(result.model_dump(mode="json"))
    trace = build_trace(
        engine="cashflow",
        version=VERSION,
        function="compute_cashflow_buckets",
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        formula_refs=_FORMULA_REFS,
    )
    return EngineResult(result=result, trace=trace)
