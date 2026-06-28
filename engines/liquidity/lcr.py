"""
LCR (Liquidity Coverage Ratio) Engine — Basel III LCR standard.

Reference: BCBS "Basel III: The Liquidity Coverage Ratio and liquidity risk
monitoring tools" (January 2013), LCR30 (HQLA) and LCR40 (Cash flows).

Formula:
    LCR = HQLA / Net Cash Outflows (30-day stress)
    HQLA = Level 1 + min(Level 2A + Level 2B, L2 cap)
    Net Cash Outflows = Total Outflows − min(Total Inflows, 75% × Total Outflows)
    Minimum LCR ≥ 100%
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from engines.common.audit import EngineResult, build_trace
from engines.common.models import HQLAPosition, InflowItem, LCRInput, OutflowItem
from engines.common.utils import canonical_hash, quantize, safe_divide

VERSION = "1.0.0"

_HAIRCUTS: dict[str, Decimal] = {
    "level_1":  Decimal("0.00"),
    "level_2a": Decimal("0.15"),
    "level_2b": Decimal("0.25"),  # equity/RMBS; bonds use 0.25 per LCR30.43
}

_FORMULA_REFS = [
    "BCBS LCR30.40 — Level 1 HQLA, 0% haircut",
    "BCBS LCR30.42 — Level 2A HQLA, 15% haircut, ≤40% of HQLA",
    "BCBS LCR30.43 — Level 2B HQLA, 25-50% haircut, ≤15% of HQLA",
    "BCBS LCR40.73 — Inflow cap: 75% of outflows",
]


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class HQLAComponent(BaseModel):
    """Per-level HQLA breakdown."""
    hqla_level: str
    asset_class: str
    gross_amount: Decimal
    haircut_rate: Decimal
    net_amount: Decimal
    cap_applied: bool = False


class OutflowComponent(BaseModel):
    """Per-category outflow breakdown."""
    category: str
    deposit_type: str | None
    customer_segment: str | None
    gross_balance: Decimal
    run_off_rate: Decimal
    net_outflow: Decimal


class InflowComponent(BaseModel):
    """Per-category inflow breakdown."""
    category: str
    asset_class: str | None
    gross_amount: Decimal
    inflow_rate: Decimal
    net_inflow: Decimal
    excluded: bool


class LCRResult(BaseModel):
    """Complete LCR computation output."""
    # HQLA
    hqla_level1: Decimal
    hqla_level2a_gross: Decimal
    hqla_level2a_net: Decimal
    hqla_level2b_gross: Decimal
    hqla_level2b_net: Decimal
    hqla_level2_cap_applied: bool
    hqla_level2b_cap_applied: bool
    hqla_total: Decimal
    # Cash flows
    total_outflows: Decimal
    total_inflows_before_cap: Decimal
    total_inflows: Decimal
    inflow_cap_applied: bool
    net_cash_outflows: Decimal
    # Result
    lcr_ratio: Decimal
    minimum_ratio: Decimal
    passes: bool
    currency: str
    # Breakdowns
    hqla_components: list[HQLAComponent]
    outflow_components: list[OutflowComponent]
    inflow_components: list[InflowComponent]


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def compute_lcr(inputs: LCRInput) -> EngineResult[LCRResult]:
    """
    Compute the Basel III Liquidity Coverage Ratio.

    All arithmetic uses Decimal to guarantee determinism.
    """
    inputs_hash = canonical_hash(inputs.model_dump(mode="json"))

    # ── Step 1: HQLA ─────────────────────────────────────────────────────────
    l1_gross = Decimal("0")
    l2a_gross = Decimal("0")
    l2b_gross = Decimal("0")
    hqla_components: list[HQLAComponent] = []

    for pos in inputs.hqla_positions:
        if pos.hqla_level == "ineligible":
            continue
        haircut = pos.haircut_override if pos.haircut_override is not None else _HAIRCUTS.get(pos.hqla_level, Decimal("0"))
        net = quantize(pos.gross_amount * (Decimal("1") - haircut))
        if pos.hqla_level == "level_1":
            l1_gross += pos.gross_amount
        elif pos.hqla_level == "level_2a":
            l2a_gross += pos.gross_amount
        elif pos.hqla_level == "level_2b":
            l2b_gross += pos.gross_amount
        hqla_components.append(HQLAComponent(
            hqla_level=pos.hqla_level,
            asset_class=pos.asset_class,
            gross_amount=pos.gross_amount,
            haircut_rate=haircut,
            net_amount=net,
        ))

    l1_net = l1_gross  # 0% haircut
    l2a_net = quantize(l2a_gross * Decimal("0.85"))
    l2b_net = quantize(l2b_gross * Decimal("0.75"))

    # Level 2 cap (LCR30.42): L2 ≤ 40% of total uncapped HQLA
    # Equivalently: L2 ≤ (2/3) × L1
    uncapped_hqla = l1_net + l2a_net + l2b_net
    max_l2 = quantize(uncapped_hqla * Decimal("0.40") / Decimal("0.60"))  # = 2/3 × L1 when no L2B
    actual_l2 = l2a_net + l2b_net
    l2_cap_applied = actual_l2 > max_l2
    if l2_cap_applied:
        # Scale down L2 proportionally: L2B sub-cap within capped L2
        l2b_cap_applied, l2a_net_final, l2b_net_final = _apply_l2_caps(l1_net, l2a_net, l2b_net)
    else:
        l2b_cap_applied, l2a_net_final, l2b_net_final = False, l2a_net, l2b_net

    hqla_total = quantize(l1_net + l2a_net_final + l2b_net_final)

    # Mark cap_applied on components
    for comp in hqla_components:
        if comp.hqla_level == "level_2a" and l2_cap_applied:
            object.__setattr__(comp, "cap_applied", True)
        if comp.hqla_level == "level_2b" and (l2b_cap_applied or l2_cap_applied):
            object.__setattr__(comp, "cap_applied", True)

    # ── Step 2: Outflows ─────────────────────────────────────────────────────
    total_outflows = Decimal("0")
    outflow_components: list[OutflowComponent] = []
    for item in inputs.outflow_items:
        net_out = quantize(item.balance * item.run_off_rate)
        total_outflows += net_out
        outflow_components.append(OutflowComponent(
            category=item.category,
            deposit_type=item.deposit_type,
            customer_segment=item.customer_segment,
            gross_balance=item.balance,
            run_off_rate=item.run_off_rate,
            net_outflow=net_out,
        ))
    total_outflows = quantize(total_outflows)

    # ── Step 3: Inflows ───────────────────────────────────────────────────────
    inflow_components: list[InflowComponent] = []
    total_inflows_before_cap = Decimal("0")
    for item in inputs.inflow_items:
        net_in = Decimal("0") if item.exclude_from_inflows else quantize(item.amount * item.inflow_rate)
        total_inflows_before_cap += net_in
        inflow_components.append(InflowComponent(
            category=item.category,
            asset_class=item.asset_class,
            gross_amount=item.amount,
            inflow_rate=item.inflow_rate,
            net_inflow=net_in,
            excluded=item.exclude_from_inflows,
        ))

    total_inflows_before_cap = quantize(total_inflows_before_cap)
    inflow_cap = quantize(total_outflows * Decimal("0.75"))
    inflow_cap_applied = total_inflows_before_cap > inflow_cap
    total_inflows = min(total_inflows_before_cap, inflow_cap)

    # ── Step 4: Net Cash Outflows ─────────────────────────────────────────────
    nco = quantize(total_outflows - total_inflows)

    # ── Step 5: LCR ratio ─────────────────────────────────────────────────────
    lcr_ratio = quantize(safe_divide(hqla_total, nco))
    passes = lcr_ratio >= inputs.minimum_ratio

    result = LCRResult(
        hqla_level1=quantize(l1_net),
        hqla_level2a_gross=quantize(l2a_gross),
        hqla_level2a_net=quantize(l2a_net_final),
        hqla_level2b_gross=quantize(l2b_gross),
        hqla_level2b_net=quantize(l2b_net_final),
        hqla_level2_cap_applied=l2_cap_applied,
        hqla_level2b_cap_applied=l2b_cap_applied,
        hqla_total=hqla_total,
        total_outflows=total_outflows,
        total_inflows_before_cap=total_inflows_before_cap,
        total_inflows=quantize(total_inflows),
        inflow_cap_applied=inflow_cap_applied,
        net_cash_outflows=nco,
        lcr_ratio=lcr_ratio,
        minimum_ratio=inputs.minimum_ratio,
        passes=passes,
        currency=inputs.currency,
        hqla_components=hqla_components,
        outflow_components=outflow_components,
        inflow_components=inflow_components,
    )

    outputs_hash = canonical_hash(result.model_dump(mode="json"))
    trace = build_trace(
        engine="lcr",
        version=VERSION,
        function="compute_lcr",
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        formula_refs=_FORMULA_REFS,
    )
    return EngineResult(result=result, trace=trace)


def _apply_l2_caps(
    l1_net: Decimal, l2a_net: Decimal, l2b_net: Decimal
) -> tuple[bool, Decimal, Decimal]:
    """Apply Level 2 cap and Level 2B sub-cap. Returns (l2b_capped, l2a_final, l2b_final)."""
    # Level 2B sub-cap: L2B ≤ 15% of uncapped_HQLA (LCR30.43)
    uncapped = l1_net + l2a_net + l2b_net
    max_l2b = quantize(uncapped * Decimal("15") / Decimal("100"))
    l2b_capped = l2b_net > max_l2b
    l2b_after_subcap = min(l2b_net, max_l2b)

    # Overall Level 2 cap: (L2A + L2B) ≤ 40% of (L1 + L2A + L2B)
    # i.e. ≤ (2/3) × L1_net  [solving the constraint]
    hqla_after_subcap = l1_net + l2a_net + l2b_after_subcap
    max_l2_total = quantize(hqla_after_subcap * Decimal("40") / Decimal("100") / Decimal("60") * Decimal("100"))
    # Simpler: max_l2_total = (2/3) × L1 is not exact; correct formula:
    # L2A + L2B ≤ 0.4/(1-0.4) × L1 = (2/3) × L1
    max_l2_total = quantize(l1_net * Decimal("2") / Decimal("3"))
    actual_l2 = l2a_net + l2b_after_subcap

    if actual_l2 > max_l2_total:
        # Scale proportionally: reduce L2A first, then L2B
        l2a_final = min(l2a_net, max_l2_total - l2b_after_subcap)
        l2a_final = max(l2a_final, Decimal("0"))
        l2b_final = min(l2b_after_subcap, max_l2_total - l2a_final)
        l2b_final = max(l2b_final, Decimal("0"))
    else:
        l2a_final = l2a_net
        l2b_final = l2b_after_subcap

    return l2b_capped, quantize(l2a_final), quantize(l2b_final)
