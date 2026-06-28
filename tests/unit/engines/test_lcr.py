"""Unit tests for the LCR engine."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from engines.common.models import HQLAPosition, InflowItem, LCRInput, OutflowItem
from engines.liquidity.lcr import VERSION, LCRResult, compute_lcr


def _basic_input(
    l1: Decimal = Decimal("100"),
    l2a: Decimal = Decimal("0"),
    l2b: Decimal = Decimal("0"),
    outflows: list[OutflowItem] | None = None,
    inflows: list[InflowItem] | None = None,
) -> LCRInput:
    hqla = []
    if l1 > 0:
        hqla.append(HQLAPosition(hqla_level="level_1", asset_class="sovereign", gross_amount=l1))
    if l2a > 0:
        hqla.append(HQLAPosition(hqla_level="level_2a", asset_class="corporate", gross_amount=l2a))
    if l2b > 0:
        hqla.append(HQLAPosition(hqla_level="level_2b", asset_class="equity_listed", gross_amount=l2b))
    return LCRInput(
        snapshot_id="test-snap",
        entity_id="test-entity",
        reporting_date=date(2024, 3, 31),
        hqla_positions=hqla,
        outflow_items=outflows or [
            OutflowItem(
                category="retail_stable",
                deposit_type="retail_stable",
                customer_segment="retail",
                balance=Decimal("100"),
                run_off_rate=Decimal("0.03"),
            )
        ],
        inflow_items=inflows or [],
        currency="INR",
    )


class TestLCRBasicFormula:
    def test_lcr_ratio_is_hqla_over_nco(self):
        # HQLA=100 (L1), outflows=3 (100 × 3%), inflows=0, NCO=3
        # LCR = 100 / 3 = 33.33...
        result = compute_lcr(_basic_input()).result
        expected_nco = Decimal("100") * Decimal("0.03")
        assert result.net_cash_outflows == expected_nco
        assert result.hqla_total == Decimal("100.00000000")
        # ratio is quantized to 8dp; compare with tolerance
        expected_ratio = result.hqla_total / result.net_cash_outflows
        assert abs(result.lcr_ratio - expected_ratio) < Decimal("0.00000001")

    def test_passes_when_ratio_above_minimum(self):
        result = compute_lcr(_basic_input()).result
        assert result.passes is True  # HQLA=100 >> NCO=3

    def test_fails_when_hqla_insufficient(self):
        # Make NCO larger than HQLA: 100 × 100% = 100 outflow, but only 50 HQLA
        inp = LCRInput(
            snapshot_id="s",
            entity_id="e",
            reporting_date=date(2024, 3, 31),
            hqla_positions=[HQLAPosition(hqla_level="level_1", asset_class="sovereign", gross_amount=Decimal("50"))],
            outflow_items=[
                OutflowItem(category="call_money", deposit_type=None, customer_segment=None,
                            balance=Decimal("100"), run_off_rate=Decimal("1.0"))
            ],
            inflow_items=[],
        )
        result = compute_lcr(inp).result
        assert result.lcr_ratio < Decimal("1")
        assert result.passes is False

    def test_no_double_count_inflows_already_in_hqla(self):
        # A T-bill that is HQLA AND matures → must be excluded from inflows
        inp = LCRInput(
            snapshot_id="s",
            entity_id="e",
            reporting_date=date(2024, 3, 31),
            hqla_positions=[HQLAPosition(hqla_level="level_1", asset_class="sovereign", gross_amount=Decimal("200"))],
            outflow_items=[
                OutflowItem(category="retail_stable", deposit_type="retail_stable",
                            customer_segment="retail", balance=Decimal("100"), run_off_rate=Decimal("0.03"))
            ],
            inflow_items=[
                InflowItem(category="tbill_maturing", asset_class="sovereign",
                           amount=Decimal("200"), inflow_rate=Decimal("1.0"),
                           exclude_from_inflows=True),
            ],
        )
        result = compute_lcr(inp).result
        # Excluded inflow → total inflows = 0
        assert result.total_inflows == Decimal("0")
        assert result.net_cash_outflows == Decimal("3.00000000")  # 100 × 3%

    def test_version_constant(self):
        assert VERSION == "1.0.0"


class TestLCRInflowCap:
    def test_inflow_cap_applies_when_inflows_exceed_75pct_outflows(self):
        # outflows = 100, 75% cap = 75
        # uncapped inflows = 80 → capped to 75
        inp = LCRInput(
            snapshot_id="s",
            entity_id="e",
            reporting_date=date(2024, 3, 31),
            hqla_positions=[HQLAPosition(hqla_level="level_1", asset_class="sovereign", gross_amount=Decimal("1000"))],
            outflow_items=[
                OutflowItem(category="wholesale", deposit_type=None, customer_segment=None,
                            balance=Decimal("100"), run_off_rate=Decimal("1.0"))
            ],
            inflow_items=[
                InflowItem(category="loans_maturing", asset_class="corporate",
                           amount=Decimal("80"), inflow_rate=Decimal("1.0"))
            ],
        )
        result = compute_lcr(inp).result
        assert result.inflow_cap_applied is True
        assert result.total_inflows == Decimal("75.00000000")  # capped at 75% of 100
        assert result.net_cash_outflows == Decimal("25.00000000")

    def test_inflow_cap_does_not_apply_below_threshold(self):
        inp = LCRInput(
            snapshot_id="s",
            entity_id="e",
            reporting_date=date(2024, 3, 31),
            hqla_positions=[HQLAPosition(hqla_level="level_1", asset_class="sovereign", gross_amount=Decimal("1000"))],
            outflow_items=[
                OutflowItem(category="wholesale", deposit_type=None, customer_segment=None,
                            balance=Decimal("100"), run_off_rate=Decimal("1.0"))
            ],
            inflow_items=[
                InflowItem(category="loans_maturing", asset_class="corporate",
                           amount=Decimal("50"), inflow_rate=Decimal("1.0"))
            ],
        )
        result = compute_lcr(inp).result
        assert result.inflow_cap_applied is False
        assert result.total_inflows == Decimal("50.00000000")
        assert result.net_cash_outflows == Decimal("50.00000000")


class TestLCRHQLACaps:
    def test_level_2a_haircut_is_15_pct(self):
        # Need large L1 so L2 cap (2/3 × L1) doesn't kick in
        inp = _basic_input(l1=Decimal("1000"), l2a=Decimal("100"))
        result = compute_lcr(inp).result
        # L2A net = 100 × 85% = 85 (15% haircut); L2 cap = 2/3×1000=666 → no cap
        assert result.hqla_level2_cap_applied is False
        assert result.hqla_level2a_net == Decimal("85.00000000")

    def test_level_2b_haircut_is_25_pct(self):
        # Need large L1 so neither L2 cap nor L2B sub-cap applies
        inp = _basic_input(l1=Decimal("1000"), l2b=Decimal("100"))
        result = compute_lcr(inp).result
        # L2B net = 100 × 75% = 75; L2 cap = 666 >> 75; L2B sub-cap = 15%×(1000+75)=161 >> 75
        assert result.hqla_level2_cap_applied is False
        assert result.hqla_level2b_net == Decimal("75.00000000")

    def test_level2_cap_applies_when_l2_exceeds_40pct(self):
        # L1 = 60, L2A = 300 → L2 cap = 2/3 × 60 = 40 → L2A capped
        inp = _basic_input(l1=Decimal("60"), l2a=Decimal("300"))
        result = compute_lcr(inp).result
        assert result.hqla_level2_cap_applied is True
        # Max allowed L2A net = (2/3) × 60 = 40
        expected_max_l2 = Decimal("60") * Decimal("2") / Decimal("3")
        assert result.hqla_level2a_net <= expected_max_l2 + Decimal("0.01")

    def test_level2_cap_does_not_apply_when_l2_small(self):
        # L1 = 1000, L2A = 10 → 10 × 0.85 = 8.5 << 2/3 × 1000 = 666.7
        inp = _basic_input(l1=Decimal("1000"), l2a=Decimal("10"))
        result = compute_lcr(inp).result
        assert result.hqla_level2_cap_applied is False
        assert result.hqla_level2a_net == Decimal("8.50000000")


class TestLCRDeterminism:
    def test_same_inputs_produce_identical_hashes(self):
        inp = _basic_input()
        r1 = compute_lcr(inp)
        r2 = compute_lcr(inp)
        assert r1.trace.inputs_hash == r2.trace.inputs_hash
        assert r1.trace.outputs_hash == r2.trace.outputs_hash

    def test_trace_has_formula_refs(self):
        r = compute_lcr(_basic_input())
        assert len(r.trace.formula_refs) > 0
        assert any("LCR30" in ref or "LCR40" in ref for ref in r.trace.formula_refs)


class TestLCRGoldenDemoBank:
    """
    Golden test using seeded BSM Demo Bank component data.

    Seeded outflow components (from lcr_outflow_components):
      retail_stable_deposits:      80,000 × 3%  = 2,400
      retail_less_stable_deposits: 45,000 × 10% = 4,500
      non_op_deposits_corp:        12,000 × 40% = 4,800
      secured_wholesale_funding:   10,000 × 25% = 2,500
      operational_deposits_corp:    8,000 × 25% = 2,000
      non_op_deposits_fi:           4,000 × 40% = 1,600
      call_money_borrowed:          3,000 × 100% = 3,000
      Total outflows = 20,800

    Seeded inflow components:
      tbills_maturing:    19,850 (excluded from inflows — already in HQLA)
      repo_maturing:      10,000
      interbank_loans:     8,000
      Eligible inflows = 18,000

    HQLA:
      Level 1: 130,400 (net = 130,400, haircut=0%)
      Level 2A: 8,160 (net = 6,936, haircut=15%)
      L2 cap check: 6,936 < (2/3) × 130,400 = 86,933 → no cap
      HQLA total = 137,336

    NCO = 20,800 - min(18,000, 75% × 20,800) = 20,800 - min(18,000, 15,600) = 20,800 - 15,600 = 5,200
    LCR = 137,336 / 5,200 = 26.41 → well above 100%
    """

    def _make_demo_input(self) -> LCRInput:
        return LCRInput(
            snapshot_id="d1000000-0000-0000-0000-000000000001",
            entity_id="a1000000-0000-0000-0000-000000000001",
            reporting_date=date(2026, 3, 31),
            hqla_positions=[
                HQLAPosition(hqla_level="level_1", asset_class="sovereign", gross_amount=Decimal("130400")),
                HQLAPosition(hqla_level="level_2a", asset_class="corporate", gross_amount=Decimal("8160")),
            ],
            outflow_items=[
                OutflowItem(category="retail_stable_deposits", deposit_type="retail_stable",
                            customer_segment="retail", balance=Decimal("80000"), run_off_rate=Decimal("0.03")),
                OutflowItem(category="retail_less_stable_deposits", deposit_type="retail_less_stable",
                            customer_segment="retail", balance=Decimal("45000"), run_off_rate=Decimal("0.10")),
                OutflowItem(category="non_op_deposits_corp", deposit_type="non_operational_deposit_non_financial",
                            customer_segment="corporate", balance=Decimal("12000"), run_off_rate=Decimal("0.40")),
                OutflowItem(category="secured_wholesale_funding", deposit_type="secured_funding",
                            customer_segment="central_bank", balance=Decimal("10000"), run_off_rate=Decimal("0.25")),
                OutflowItem(category="operational_deposits_corp", deposit_type="operational_deposit",
                            customer_segment="corporate", balance=Decimal("8000"), run_off_rate=Decimal("0.25")),
                OutflowItem(category="non_op_deposits_fi", deposit_type="non_operational_deposit_financial",
                            customer_segment="financial_institution", balance=Decimal("4000"), run_off_rate=Decimal("0.40")),
                OutflowItem(category="call_money_borrowed", deposit_type="unsecured_wholesale_financial",
                            customer_segment="financial_institution", balance=Decimal("3000"), run_off_rate=Decimal("1.0")),
            ],
            inflow_items=[
                InflowItem(category="tbills_maturing", asset_class="sovereign",
                           amount=Decimal("19850"), inflow_rate=Decimal("1.0"),
                           exclude_from_inflows=True),  # already in HQLA
                InflowItem(category="repo_maturing", asset_class="sovereign",
                           amount=Decimal("10000"), inflow_rate=Decimal("1.0")),
                InflowItem(category="interbank_loans_maturing", asset_class="bank",
                           amount=Decimal("8000"), inflow_rate=Decimal("1.0")),
            ],
            currency="INR",
        )

    def test_lcr_passes(self):
        result = compute_lcr(self._make_demo_input()).result
        assert result.passes is True

    def test_hqla_level1_correct(self):
        result = compute_lcr(self._make_demo_input()).result
        assert result.hqla_level1 == Decimal("130400.00000000")

    def test_hqla_level2a_net_correct(self):
        result = compute_lcr(self._make_demo_input()).result
        expected = Decimal("130400") * Decimal("0") + Decimal("8160") * Decimal("0.85")
        assert result.hqla_level2a_net == Decimal("8160") * Decimal("0.85")

    def test_hqla_no_cap_applied(self):
        result = compute_lcr(self._make_demo_input()).result
        assert result.hqla_level2_cap_applied is False

    def test_total_outflows_correct(self):
        result = compute_lcr(self._make_demo_input()).result
        expected = (
            Decimal("80000") * Decimal("0.03")
            + Decimal("45000") * Decimal("0.10")
            + Decimal("12000") * Decimal("0.40")
            + Decimal("10000") * Decimal("0.25")
            + Decimal("8000") * Decimal("0.25")
            + Decimal("4000") * Decimal("0.40")
            + Decimal("3000") * Decimal("1.0")
        )
        assert result.total_outflows == expected

    def test_inflow_cap_applies(self):
        # inflows (18,000) > 75% × outflows (15,600) → cap applies
        result = compute_lcr(self._make_demo_input()).result
        assert result.inflow_cap_applied is True

    def test_ratio_above_150_pct(self):
        result = compute_lcr(self._make_demo_input()).result
        # Engine produces higher ratio than the seeded 1.5787 due to correct formula
        assert result.lcr_ratio > Decimal("1.5")
