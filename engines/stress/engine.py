"""
Stress Testing Engine.

Takes baseline compute inputs (LCR, NSFR, Capital) and a set of scenario
parameters, applies the shocks via the Scenario Engine, re-runs each engine,
and returns a structured comparison of baseline vs. stressed results.

This engine orchestrates the other compute engines — it calls lcr, nsfr, and
capital engines with shocked inputs and collects the deltas.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from engines.capital.engine import CapitalResult, compute_capital
from engines.common.audit import EngineResult, build_trace
from engines.common.models import StressTestInput
from engines.common.utils import canonical_hash, quantize
from engines.liquidity.lcr import LCRResult, compute_lcr
from engines.liquidity.nsfr import NSFRResult, compute_nsfr
from engines.stress.scenario import apply_capital_shocks, apply_lcr_shocks, apply_nsfr_shocks

VERSION = "1.0.0"

_FORMULA_REFS = [
    "BCBS Stress testing principles (2018)",
    "RBI Stress Testing framework for banks",
    "Scenario application: absolute / relative / replace shock types",
]


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class MetricDelta(BaseModel):
    """Before/after comparison for a single metric."""
    baseline: Decimal | None
    stressed: Decimal | None
    delta: Decimal | None
    baseline_passes: bool | None
    stressed_passes: bool | None
    threshold: Decimal | None


class StressTestResult(BaseModel):
    """Complete stress test comparison output."""
    scenario_code: str
    # LCR impact
    lcr: MetricDelta
    # Capital impact
    cet1_ratio: MetricDelta
    total_capital_ratio: MetricDelta
    leverage_ratio: MetricDelta
    # NSFR impact
    nsfr: MetricDelta
    # Detailed results
    baseline_lcr_result: LCRResult | None = None
    stressed_lcr_result: LCRResult | None = None
    baseline_capital_result: CapitalResult | None = None
    stressed_capital_result: CapitalResult | None = None
    baseline_nsfr_result: NSFRResult | None = None
    stressed_nsfr_result: NSFRResult | None = None
    parameters_applied: list[dict]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _delta(base: Decimal | None, stressed: Decimal | None) -> Decimal | None:
    if base is None or stressed is None:
        return None
    return quantize(stressed - base)


def _make_delta(
    baseline: Decimal | None,
    stressed: Decimal | None,
    baseline_passes: bool | None,
    stressed_passes: bool | None,
    threshold: Decimal | None,
) -> MetricDelta:
    return MetricDelta(
        baseline=baseline,
        stressed=stressed,
        delta=_delta(baseline, stressed),
        baseline_passes=baseline_passes,
        stressed_passes=stressed_passes,
        threshold=threshold,
    )


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def compute_stress_test(inputs: StressTestInput) -> EngineResult[StressTestResult]:
    """
    Run a stress scenario against baseline LCR, NSFR, and Capital inputs.

    The function:
    1. Runs baseline engines on the unshocked inputs.
    2. Applies scenario parameters to get shocked inputs.
    3. Re-runs engines on shocked inputs.
    4. Computes deltas.
    """
    inputs_hash = canonical_hash(inputs.model_dump(mode="json"))

    params_list = [p.model_dump(mode="json") for p in inputs.parameters]

    # ── LCR ──────────────────────────────────────────────────────────────────
    bl_lcr_result: LCRResult | None = None
    st_lcr_result: LCRResult | None = None

    if inputs.baseline_lcr_input is not None:
        bl_lcr = compute_lcr(inputs.baseline_lcr_input)
        bl_lcr_result = bl_lcr.result

        stressed_lcr_input = apply_lcr_shocks(inputs.baseline_lcr_input, list(inputs.parameters))
        st_lcr = compute_lcr(stressed_lcr_input)
        st_lcr_result = st_lcr.result

    lcr_delta = _make_delta(
        bl_lcr_result.lcr_ratio if bl_lcr_result else None,
        st_lcr_result.lcr_ratio if st_lcr_result else None,
        bl_lcr_result.passes if bl_lcr_result else None,
        st_lcr_result.passes if st_lcr_result else None,
        inputs.baseline_lcr_input.minimum_ratio if inputs.baseline_lcr_input else None,
    )

    # ── NSFR ─────────────────────────────────────────────────────────────────
    bl_nsfr_result: NSFRResult | None = None
    st_nsfr_result: NSFRResult | None = None

    if inputs.baseline_nsfr_input is not None:
        bl_nsfr = compute_nsfr(inputs.baseline_nsfr_input)
        bl_nsfr_result = bl_nsfr.result

        stressed_nsfr_input = apply_nsfr_shocks(inputs.baseline_nsfr_input, list(inputs.parameters))
        st_nsfr = compute_nsfr(stressed_nsfr_input)
        st_nsfr_result = st_nsfr.result

    nsfr_delta = _make_delta(
        bl_nsfr_result.nsfr_ratio if bl_nsfr_result else None,
        st_nsfr_result.nsfr_ratio if st_nsfr_result else None,
        bl_nsfr_result.passes if bl_nsfr_result else None,
        st_nsfr_result.passes if st_nsfr_result else None,
        inputs.baseline_nsfr_input.minimum_ratio if inputs.baseline_nsfr_input else None,
    )

    # ── Capital ───────────────────────────────────────────────────────────────
    bl_cap_result: CapitalResult | None = None
    st_cap_result: CapitalResult | None = None

    if inputs.baseline_capital_input is not None:
        bl_cap = compute_capital(inputs.baseline_capital_input)
        bl_cap_result = bl_cap.result

        stressed_cap_input = apply_capital_shocks(inputs.baseline_capital_input, list(inputs.parameters))
        st_cap = compute_capital(stressed_cap_input)
        st_cap_result = st_cap.result

    cet1_delta = _make_delta(
        bl_cap_result.cet1_ratio if bl_cap_result else None,
        st_cap_result.cet1_ratio if st_cap_result else None,
        bl_cap_result.passes_cet1 if bl_cap_result else None,
        st_cap_result.passes_cet1 if st_cap_result else None,
        inputs.baseline_capital_input.cet1_minimum if inputs.baseline_capital_input else None,
    )
    tc_delta = _make_delta(
        bl_cap_result.total_capital_ratio if bl_cap_result else None,
        st_cap_result.total_capital_ratio if st_cap_result else None,
        bl_cap_result.passes_total if bl_cap_result else None,
        st_cap_result.passes_total if st_cap_result else None,
        inputs.baseline_capital_input.total_minimum if inputs.baseline_capital_input else None,
    )
    lev_delta = _make_delta(
        bl_cap_result.leverage_ratio if bl_cap_result else None,
        st_cap_result.leverage_ratio if st_cap_result else None,
        bl_cap_result.passes_leverage if bl_cap_result else None,
        st_cap_result.passes_leverage if st_cap_result else None,
        inputs.baseline_capital_input.leverage_minimum if inputs.baseline_capital_input else None,
    )

    result = StressTestResult(
        scenario_code=inputs.scenario_code,
        lcr=lcr_delta,
        cet1_ratio=cet1_delta,
        total_capital_ratio=tc_delta,
        leverage_ratio=lev_delta,
        nsfr=nsfr_delta,
        baseline_lcr_result=bl_lcr_result,
        stressed_lcr_result=st_lcr_result,
        baseline_capital_result=bl_cap_result,
        stressed_capital_result=st_cap_result,
        baseline_nsfr_result=bl_nsfr_result,
        stressed_nsfr_result=st_nsfr_result,
        parameters_applied=params_list,
    )

    outputs_hash = canonical_hash(result.model_dump(mode="json"))
    trace = build_trace(
        engine="stress",
        version=VERSION,
        function="compute_stress_test",
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        formula_refs=_FORMULA_REFS,
    )
    return EngineResult(result=result, trace=trace)
