"""Unit tests for the Stress Testing and Scenario engines."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from engines.capital.engine import compute_capital
from engines.common.models import (
    CapitalInput,
    HQLAPosition,
    LCRInput,
    NSFRAssetItem,
    NSFRFundingItem,
    NSFRInput,
    OutflowItem,
    RWAPositionItem,
    ScenarioParameter,
    StressTestInput,
)
from engines.liquidity.lcr import compute_lcr
from engines.stress.engine import VERSION as STRESS_VERSION, compute_stress_test
from engines.stress.scenario import (
    VERSION as SCENARIO_VERSION,
    apply_capital_shocks,
    apply_lcr_shocks,
    apply_nsfr_shocks,
)


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def _lcr_input() -> LCRInput:
    return LCRInput(
        snapshot_id="s",
        entity_id="e",
        reporting_date=date(2024, 3, 31),
        hqla_positions=[
            HQLAPosition(hqla_level="level_1", asset_class="sovereign", gross_amount=Decimal("1000"))
        ],
        outflow_items=[
            OutflowItem(category="retail_stable", deposit_type="retail_stable",
                        customer_segment="retail", balance=Decimal("200"), run_off_rate=Decimal("0.03")),
        ],
        inflow_items=[],
        currency="INR",
    )


def _nsfr_input() -> NSFRInput:
    return NSFRInput(
        snapshot_id="s",
        entity_id="e",
        reporting_date=date(2024, 3, 31),
        funding_items=[
            NSFRFundingItem(category="tier1", balance=Decimal("200"), asf_factor=Decimal("1.0"),
                            maturity_bucket="gt_1y"),
        ],
        asset_items=[
            NSFRAssetItem(category="loans", balance=Decimal("100"), rsf_factor=Decimal("1.0"),
                          maturity_bucket="gt_1y"),
        ],
        currency="INR",
    )


def _capital_input() -> CapitalInput:
    return CapitalInput(
        snapshot_id="s",
        entity_id="e",
        reporting_date=date(2024, 3, 31),
        rwa_positions=[
            RWAPositionItem(position_id="p1", asset_class="loans", credit_grade="BBB",
                            jurisdiction="IN", booked_amount=Decimal("100"), risk_weight=Decimal("1.0")),
        ],
        rwa_market=Decimal("0"),
        rwa_operational=Decimal("0"),
        cet1_capital=Decimal("20"),
        additional_tier1=Decimal("0"),
        tier2_capital=Decimal("0"),
        total_exposure=Decimal("500"),
        cet1_minimum=Decimal("0.045"),
        tier1_minimum=Decimal("0.060"),
        total_minimum=Decimal("0.08"),
        leverage_minimum=Decimal("0.03"),
        currency="INR",
    )


# ---------------------------------------------------------------------------
# Scenario shock tests
# ---------------------------------------------------------------------------

class TestApplyShock:
    def test_relative_outflow_shock_increases_run_off_rate(self):
        param = ScenarioParameter(
            parameter_type="liquidity",
            parameter_name="outflow_shock",
            shock_type="relative",
            shock_value=Decimal("0.5"),   # +50%
        )
        shocked = apply_lcr_shocks(_lcr_input(), [param])
        # Original run_off_rate=0.03, +50% → 0.045
        assert shocked.outflow_items[0].run_off_rate == Decimal("0.045")

    def test_absolute_outflow_shock(self):
        param = ScenarioParameter(
            parameter_type="liquidity",
            parameter_name="outflow_shock",
            shock_type="absolute",
            shock_value=Decimal("0.10"),
        )
        shocked = apply_lcr_shocks(_lcr_input(), [param])
        # 0.03 + 0.10 = 0.13
        assert shocked.outflow_items[0].run_off_rate == Decimal("0.13")

    def test_replace_outflow_shock(self):
        param = ScenarioParameter(
            parameter_type="liquidity",
            parameter_name="outflow_shock",
            shock_type="replace",
            shock_value=Decimal("0.20"),
        )
        shocked = apply_lcr_shocks(_lcr_input(), [param])
        assert shocked.outflow_items[0].run_off_rate == Decimal("0.20")

    def test_outflow_shock_capped_at_100pct(self):
        param = ScenarioParameter(
            parameter_type="liquidity",
            parameter_name="outflow_shock",
            shock_type="absolute",
            shock_value=Decimal("2.0"),   # would push rate to 2.03
        )
        shocked = apply_lcr_shocks(_lcr_input(), [param])
        assert shocked.outflow_items[0].run_off_rate == Decimal("1")

    def test_hqla_shock_reduces_hqla(self):
        param = ScenarioParameter(
            parameter_type="liquidity",
            parameter_name="hqla_shock",
            shock_type="relative",
            shock_value=Decimal("-0.30"),   # -30%
        )
        shocked = apply_lcr_shocks(_lcr_input(), [param])
        # 1000 × (1 - 0.30) = 700
        assert shocked.hqla_positions[0].gross_amount == Decimal("700")

    def test_hqla_shock_floored_at_zero(self):
        param = ScenarioParameter(
            parameter_type="liquidity",
            parameter_name="hqla_shock",
            shock_type="relative",
            shock_value=Decimal("-2.0"),   # would go negative
        )
        shocked = apply_lcr_shocks(_lcr_input(), [param])
        assert shocked.hqla_positions[0].gross_amount == Decimal("0")

    def test_nsfr_asf_shock_scales_asf_factor(self):
        param = ScenarioParameter(
            parameter_type="liquidity",
            parameter_name="asf_shock",
            shock_type="relative",
            shock_value=Decimal("-0.10"),
        )
        shocked = apply_nsfr_shocks(_nsfr_input(), [param])
        # 1.0 × (1 - 0.10) = 0.9
        assert shocked.funding_items[0].asf_factor == Decimal("0.9")

    def test_capital_rwa_shock_scales_risk_weight(self):
        param = ScenarioParameter(
            parameter_type="capital",
            parameter_name="rwa_shock",
            shock_type="relative",
            shock_value=Decimal("0.20"),   # +20%
        )
        shocked = apply_capital_shocks(_capital_input(), [param])
        # 1.0 × 1.20 = 1.20
        assert shocked.rwa_positions[0].risk_weight == Decimal("1.2")

    def test_non_matching_parameter_type_ignored(self):
        param = ScenarioParameter(
            parameter_type="credit",   # not "liquidity"
            parameter_name="outflow_shock",
            shock_type="absolute",
            shock_value=Decimal("1.0"),
        )
        shocked = apply_lcr_shocks(_lcr_input(), [param])
        # run_off_rate unchanged
        assert shocked.outflow_items[0].run_off_rate == Decimal("0.03")

    def test_scenario_version(self):
        assert SCENARIO_VERSION == "1.0.0"


# ---------------------------------------------------------------------------
# Stress test engine tests
# ---------------------------------------------------------------------------

class TestStressTestEngine:
    def _stress_input_lcr_only(self, shock: Decimal) -> StressTestInput:
        return StressTestInput(
            scenario_code="SC-TEST-LCR",
            snapshot_id="s",
            entity_id="e",
            reporting_date=date(2024, 3, 31),
            baseline_lcr_input=_lcr_input(),
            baseline_nsfr_input=None,
            baseline_capital_input=None,
            parameters=[
                ScenarioParameter(
                    parameter_type="liquidity",
                    parameter_name="outflow_shock",
                    shock_type="relative",
                    shock_value=shock,
                )
            ],
            currency="INR",
        )

    def test_lcr_delta_is_stressed_minus_baseline(self):
        inp = self._stress_input_lcr_only(Decimal("1.0"))  # double outflows
        result = compute_stress_test(inp).result
        assert result.lcr.delta is not None
        assert result.lcr.stressed < result.lcr.baseline

    def test_no_nsfr_metrics_when_nsfr_not_provided(self):
        inp = self._stress_input_lcr_only(Decimal("0.5"))
        result = compute_stress_test(inp).result
        assert result.nsfr.baseline is None
        assert result.nsfr.stressed is None
        assert result.nsfr.delta is None

    def test_scenario_code_preserved(self):
        inp = self._stress_input_lcr_only(Decimal("0.5"))
        result = compute_stress_test(inp).result
        assert result.scenario_code == "SC-TEST-LCR"

    def test_parameters_applied_recorded(self):
        inp = self._stress_input_lcr_only(Decimal("0.5"))
        result = compute_stress_test(inp).result
        assert len(result.parameters_applied) == 1

    def test_full_stress_test_all_engines(self):
        inp = StressTestInput(
            scenario_code="SC-FULL",
            snapshot_id="s",
            entity_id="e",
            reporting_date=date(2024, 3, 31),
            baseline_lcr_input=_lcr_input(),
            baseline_nsfr_input=_nsfr_input(),
            baseline_capital_input=_capital_input(),
            parameters=[
                ScenarioParameter(
                    parameter_type="liquidity",
                    parameter_name="outflow_shock",
                    shock_type="relative",
                    shock_value=Decimal("0.5"),
                ),
                ScenarioParameter(
                    parameter_type="capital",
                    parameter_name="rwa_shock",
                    shock_type="relative",
                    shock_value=Decimal("0.25"),
                ),
            ],
            currency="INR",
        )
        result = compute_stress_test(inp).result
        # All metrics populated
        assert result.lcr.delta is not None
        assert result.nsfr.delta is not None
        assert result.cet1_ratio.delta is not None
        assert result.total_capital_ratio.delta is not None
        assert result.leverage_ratio.delta is not None
        # Shocked ratios are worse
        assert result.lcr.stressed < result.lcr.baseline
        assert result.cet1_ratio.stressed < result.cet1_ratio.baseline
        # Detailed results attached
        assert result.baseline_lcr_result is not None
        assert result.stressed_lcr_result is not None

    def test_stress_version(self):
        assert STRESS_VERSION == "1.0.0"

    def test_stress_determinism(self):
        inp = self._stress_input_lcr_only(Decimal("0.5"))
        r1 = compute_stress_test(inp)
        r2 = compute_stress_test(inp)
        assert r1.trace.inputs_hash == r2.trace.inputs_hash
        assert r1.trace.outputs_hash == r2.trace.outputs_hash


class TestStressTestGoldenDemoBank:
    """Stress test using Demo Bank baseline capital — verifies directional correctness."""

    def _capital_inp(self) -> CapitalInput:
        return CapitalInput(
            snapshot_id="d1000000-0000-0000-0000-000000000001",
            entity_id="a1000000-0000-0000-0000-000000000001",
            reporting_date=date(2026, 3, 31),
            rwa_positions=[
                RWAPositionItem(position_id="p1", asset_class="loans_corporate", credit_grade="BBB",
                                jurisdiction="IN", booked_amount=Decimal("100000"), risk_weight=Decimal("0.75")),
                RWAPositionItem(position_id="p2", asset_class="loans_retail", credit_grade="RETAIL",
                                jurisdiction="IN", booked_amount=Decimal("80000"), risk_weight=Decimal("0.75")),
                RWAPositionItem(position_id="p3", asset_class="other_assets", credit_grade="UNRATED",
                                jurisdiction="IN", booked_amount=Decimal("63500"), risk_weight=Decimal("1.0")),
                RWAPositionItem(position_id="p4", asset_class="sovereign", credit_grade="AAA",
                                jurisdiction="IN", booked_amount=Decimal("130400"), risk_weight=Decimal("0.0")),
            ],
            rwa_market=Decimal("0"),
            rwa_operational=Decimal("0"),
            cet1_capital=Decimal("22750"),
            additional_tier1=Decimal("3250"),
            tier2_capital=Decimal("6500"),
            total_exposure=Decimal("312500"),
            cet1_minimum=Decimal("0.045"),
            tier1_minimum=Decimal("0.060"),
            total_minimum=Decimal("0.08"),
            leverage_minimum=Decimal("0.03"),
            currency="INR",
        )

    def test_rwa_shock_reduces_cet1_ratio(self):
        inp = StressTestInput(
            scenario_code="SC-CAPITAL-STRESS",
            snapshot_id="d1000000-0000-0000-0000-000000000001",
            entity_id="a1000000-0000-0000-0000-000000000001",
            reporting_date=date(2026, 3, 31),
            baseline_lcr_input=None,
            baseline_nsfr_input=None,
            baseline_capital_input=self._capital_inp(),
            parameters=[
                ScenarioParameter(
                    parameter_type="capital",
                    parameter_name="rwa_shock",
                    shock_type="relative",
                    shock_value=Decimal("0.30"),  # +30% RWA
                ),
            ],
            currency="INR",
        )
        result = compute_stress_test(inp).result
        # Baseline passes; stressed ratio is lower
        assert result.cet1_ratio.baseline_passes is True
        assert result.cet1_ratio.stressed < result.cet1_ratio.baseline
        assert result.cet1_ratio.delta < Decimal("0")

    def test_baseline_capital_passes(self):
        inp = StressTestInput(
            scenario_code="SC-BASELINE-CHECK",
            snapshot_id="d1000000-0000-0000-0000-000000000001",
            entity_id="a1000000-0000-0000-0000-000000000001",
            reporting_date=date(2026, 3, 31),
            baseline_lcr_input=None,
            baseline_nsfr_input=None,
            baseline_capital_input=self._capital_inp(),
            parameters=[],
            currency="INR",
        )
        result = compute_stress_test(inp).result
        assert result.cet1_ratio.baseline_passes is True
        assert result.total_capital_ratio.baseline_passes is True
        assert result.leverage_ratio.baseline_passes is True
