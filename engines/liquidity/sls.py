"""
Structural Liquidity Statement (SLS) Engine — RBI DSB-II format.

Reference: RBI Master Direction — Basel III Framework on Liquidity Standards
(DSB-II return), which requires banks to report maturity profiles in 10 time
buckets using a 30-day stress scenario horizon extended to structural view.

Time buckets (RBI DSB-II):
    0_1d     0–1 days
    1_7d     >1–7 days
    7_14d    >7–14 days
    14_28d   >14–28 days
    28d_3m   >28 days–3 months  (≤92 days)
    3m_6m    >3–6 months        (≤183 days)
    6m_1y    >6 months–1 year   (≤365 days)
    1y_3y    >1–3 years         (≤1095 days)
    3y_5y    >3–5 years         (≤1826 days)
    gt_5y    >5 years
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
    "RBI Master Direction Basel III Framework on Liquidity Standards (2019)",
]

SLS_BUCKETS: list[tuple[str, int, int]] = [
    # (bucket_name, min_days_exclusive, max_days_inclusive)
    ("0_1d",    0,    1),
    ("1_7d",    1,    7),
    ("7_14d",   7,   14),
    ("14_28d",  14,  28),
    ("28d_3m",  28,  92),
    ("3m_6m",   92, 183),
    ("6m_1y",  183, 365),
    ("1y_3y",  365, 1095),
    ("3y_5y", 1095, 1826),
    ("gt_5y", 1826, 999999),
]


def _assign_bucket(days: int) -> str:
    """Assign a cashflow to a time bucket based on days from reporting date."""
    for name, lo, hi in SLS_BUCKETS:
        if lo < days <= hi:
            return name
    return "gt_5y"


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class SLSBucket(BaseModel):
    """Per-time-bucket SLS aggregation."""
    time_bucket: str
    bucket_order: int
    total_inflows: Decimal
    total_outflows: Decimal
    net_position: Decimal
    cumulative_net: Decimal
    currency: str


class SLSResult(BaseModel):
    """Complete SLS computation output."""
    buckets: list[SLSBucket]
    total_inflows: Decimal
    total_outflows: Decimal
    net_position: Decimal
    currency: str


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def compute_sls(inputs: CashflowInput) -> EngineResult[SLSResult]:
    """
    Bucket all cashflows into RBI DSB-II time bands.

    Positive cashflows (amount > 0) = inflows (asset maturities / receipts).
    Negative cashflows (amount < 0) = outflows (liability maturities / payments).
    Cashflows with dates ≤ reporting_date are placed in bucket "0_1d" (past-due / same-day).
    """
    inputs_hash = canonical_hash(inputs.model_dump(mode="json"))

    # Initialise buckets
    inflows: dict[str, Decimal] = {b[0]: Decimal("0") for b in SLS_BUCKETS}
    outflows: dict[str, Decimal] = {b[0]: Decimal("0") for b in SLS_BUCKETS}

    for cf in inputs.cashflows:
        days = (cf.cashflow_date - inputs.reporting_date).days
        # Past-due or same-day → bucket 1 (0_1d)
        days = max(days, 0)
        # Bucket 0 days as "0_1d" (≤1 day)
        bucket = "0_1d" if days == 0 else _assign_bucket(days)
        if cf.amount >= Decimal("0"):
            inflows[bucket] += cf.amount
        else:
            outflows[bucket] += abs(cf.amount)

    # Build ordered bucket list with cumulative net
    result_buckets: list[SLSBucket] = []
    cumulative = Decimal("0")
    grand_in = Decimal("0")
    grand_out = Decimal("0")

    for order, (name, _, _) in enumerate(SLS_BUCKETS, start=1):
        bucket_in = quantize(inflows[name])
        bucket_out = quantize(outflows[name])
        net = quantize(bucket_in - bucket_out)
        cumulative = quantize(cumulative + net)
        grand_in += bucket_in
        grand_out += bucket_out
        result_buckets.append(SLSBucket(
            time_bucket=name,
            bucket_order=order,
            total_inflows=bucket_in,
            total_outflows=bucket_out,
            net_position=net,
            cumulative_net=cumulative,
            currency=inputs.currency,
        ))

    result = SLSResult(
        buckets=result_buckets,
        total_inflows=quantize(grand_in),
        total_outflows=quantize(grand_out),
        net_position=quantize(grand_in - grand_out),
        currency=inputs.currency,
    )

    outputs_hash = canonical_hash(result.model_dump(mode="json"))
    trace = build_trace(
        engine="sls",
        version=VERSION,
        function="compute_sls",
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        formula_refs=_FORMULA_REFS,
    )
    return EngineResult(result=result, trace=trace)
