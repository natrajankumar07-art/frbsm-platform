"""Unit tests for the Capital Adequacy engine."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from engines.capital.engine import VERSION, compute_capital
from engines.common.models import CapitalInput, RWAPositionItem


def _simple_capital(
    cet1: Decimal,
    at1: Decimal,
    t2: Decimal,
    rwa_credit: Decimal,
    total_exposure: Decimal | None = None,
) -> CapitalInput:
    return CapitalInput(
        snapshot_id="s",
        entity_id="e",
        reporting_date=date(2024, 3, 31),
        rwa_positions=[
            RWAPositionItem(
                position_id="p1",
                asset_class="loans_corporate",
                credit_grade="BBB",
                jurisdiction="IN",
                booked_amount=rwa_credit,
                risk_weight=Decimal("1.0"),
            )
        ],
        rwa_market=Decimal("0"),
        rwa_operational=Decimal("0"),
        cet1_capital=cet1,
        additional_tier1=at1,
        tier2_capital=t2,
        total_exposure=total_exposure or (cet1 + at1 + t2) * Decimal("10"),
        cet1_minimum=Decimal("0.045"),
        tier1_minimum=Decimal("0.060"),
        total_minimum=Decimal("0.08"),
        leverage_minimum=Decimal("0.03"),
        currency="INR",
    )


class TestCapitalBasicFormula:
    def test_cet1_ratio_formula(self):
        # CET1=40, RWA=100 → 0.4
        result = compute_capital(_simple_capital(Decimal("40"), Decimal("0"), Decimal("0"), Decimal("100"))).result
        assert result.cet1_ratio == Decimal("0.40000000")

    def test_tier1_ratio_includes_at1(self):
        # CET1=30, AT1=10, RWA=100 → T1 ratio = 0.4
        result = compute_capital(_simple_capital(Decimal("30"), Decimal("10"), Decimal("0"), Decimal("100"))).result
        assert result.tier1_ratio == Decimal("0.40000000")

    def test_total_capital_ratio_includes_t2(self):
        # CET1=30, AT1=10, T2=10, RWA=100 → TC ratio = 0.5
        result = compute_capital(_simple_capital(Decimal("30"), Decimal("10"), Decimal("10"), Decimal("100"))).result
        assert result.total_capital_ratio == Decimal("0.50000000")

    def test_rwa_credit_sum_of_positions(self):
        inp = CapitalInput(
            snapshot_id="s",
            entity_id="e",
            reporting_date=date(2024, 3, 31),
            rwa_positions=[
                RWAPositionItem(position_id="p1", asset_class="corp", credit_grade="A",
                                jurisdiction="IN", booked_amount=Decimal("100"), risk_weight=Decimal("0.75")),
                RWAPositionItem(position_id="p2", asset_class="sov", credit_grade="AAA",
                                jurisdiction="IN", booked_amount=Decimal("200"), risk_weight=Decimal("0")),
            ],
            rwa_market=Decimal("10"),
            rwa_operational=Decimal("5"),
            cet1_capital=Decimal("100"),
            additional_tier1=Decimal("0"),
            tier2_capital=Decimal("0"),
            total_exposure=Decimal("1000"),
        )
        result = compute_capital(inp).result
        assert result.rwa_credit == Decimal("75.00000000")   # 100×0.75 + 200×0
        assert result.total_rwa == Decimal("90.00000000")    # 75 + 10 + 5

    def test_leverage_ratio_t1_over_exposure(self):
        # T1=26, exposure=312,500 → 0.0000832
        inp = _simple_capital(Decimal("20"), Decimal("6"), Decimal("0"), Decimal("100"), Decimal("1000"))
        result = compute_capital(inp).result
        assert result.leverage_ratio == Decimal("26") / Decimal("1000")

    def test_passes_all_when_well_capitalised(self):
        result = compute_capital(_simple_capital(Decimal("50"), Decimal("10"), Decimal("10"), Decimal("100"))).result
        assert result.passes_cet1 is True
        assert result.passes_tier1 is True
        assert result.passes_total is True
        assert result.passes_all is True

    def test_fails_when_undercapitalised(self):
        # CET1=1, RWA=1000 → CET1 ratio = 0.001 < 4.5%
        result = compute_capital(_simple_capital(Decimal("1"), Decimal("0"), Decimal("0"), Decimal("1000"))).result
        assert result.passes_cet1 is False
        assert result.passes_all is False

    def test_version_constant(self):
        assert VERSION == "1.0.0"


class TestCapitalDeterminism:
    def test_same_inputs_identical_hashes(self):
        inp = _simple_capital(Decimal("50"), Decimal("10"), Decimal("10"), Decimal("500"))
        r1 = compute_capital(inp)
        r2 = compute_capital(inp)
        assert r1.trace.inputs_hash == r2.trace.inputs_hash
        assert r1.trace.outputs_hash == r2.trace.outputs_hash


class TestCapitalGoldenDemoBank:
    """
    Golden test using seeded BSM Demo Bank capital data.

    From seeded capital_results (snapshot 2026-03-31):
      CET1=22,750   AT1=3,250   T2=6,500
      RWA=202,500
      CET1r≈0.1123  T1r≈0.1283  TCR≈0.1605  Lev≈0.0832

    Leverage: T1/TotalExposure = 26,000/312,500 = 0.0832
    Total exposure = 312,500

    RWA positions to total 202,500:
      loans_corporate  100,000 × 0.75 = 75,000
      loans_retail      80,000 × 0.75 = 60,000
      corporate_bonds   20,000 × 0.20 = 4,000
      other_assets      63,500 × 1.00 = 63,500
      sovereign_bonds  130,400 × 0.00 = 0
      Total credit RWA = 202,500 (market=0, operational=0)
    """

    def _demo_input(self) -> CapitalInput:
        return CapitalInput(
            snapshot_id="d1000000-0000-0000-0000-000000000001",
            entity_id="a1000000-0000-0000-0000-000000000001",
            reporting_date=date(2026, 3, 31),
            rwa_positions=[
                RWAPositionItem(position_id="p1", asset_class="loans_corporate",
                                credit_grade="BBB", jurisdiction="IN",
                                booked_amount=Decimal("100000"), risk_weight=Decimal("0.75")),
                RWAPositionItem(position_id="p2", asset_class="loans_retail",
                                credit_grade="RETAIL", jurisdiction="IN",
                                booked_amount=Decimal("80000"), risk_weight=Decimal("0.75")),
                RWAPositionItem(position_id="p3", asset_class="corporate_bonds",
                                credit_grade="A", jurisdiction="IN",
                                booked_amount=Decimal("20000"), risk_weight=Decimal("0.20")),
                RWAPositionItem(position_id="p4", asset_class="other_assets",
                                credit_grade="UNRATED", jurisdiction="IN",
                                booked_amount=Decimal("63500"), risk_weight=Decimal("1.0")),
                RWAPositionItem(position_id="p5", asset_class="sovereign_bonds",
                                credit_grade="AAA", jurisdiction="IN",
                                booked_amount=Decimal("130400"), risk_weight=Decimal("0.0")),
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

    def test_rwa_credit_equals_202500(self):
        result = compute_capital(self._demo_input()).result
        assert result.rwa_credit == Decimal("202500.00000000")

    def test_total_rwa_equals_202500(self):
        result = compute_capital(self._demo_input()).result
        assert result.total_rwa == Decimal("202500.00000000")

    def test_tier1_capital_is_26000(self):
        result = compute_capital(self._demo_input()).result
        assert result.tier1_capital == Decimal("26000.00000000")

    def test_total_capital_is_32500(self):
        result = compute_capital(self._demo_input()).result
        assert result.total_capital == Decimal("32500.00000000")

    def test_cet1_ratio_approx_0_1123(self):
        result = compute_capital(self._demo_input()).result
        expected = Decimal("22750") / Decimal("202500")
        assert abs(result.cet1_ratio - expected) < Decimal("0.0001")

    def test_tier1_ratio_approx_0_1283(self):
        result = compute_capital(self._demo_input()).result
        expected = Decimal("26000") / Decimal("202500")
        assert abs(result.tier1_ratio - expected) < Decimal("0.0001")

    def test_total_capital_ratio_approx_0_1605(self):
        result = compute_capital(self._demo_input()).result
        expected = Decimal("32500") / Decimal("202500")
        assert abs(result.total_capital_ratio - expected) < Decimal("0.0001")

    def test_leverage_ratio_approx_0_0832(self):
        result = compute_capital(self._demo_input()).result
        expected = Decimal("26000") / Decimal("312500")
        assert abs(result.leverage_ratio - expected) < Decimal("0.0001")

    def test_passes_all_minimums(self):
        result = compute_capital(self._demo_input()).result
        assert result.passes_cet1 is True
        assert result.passes_tier1 is True
        assert result.passes_total is True
        assert result.passes_leverage is True
        assert result.passes_all is True
