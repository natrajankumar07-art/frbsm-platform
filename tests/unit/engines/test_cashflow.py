"""Unit tests for the Cashflow and Liquidity Gap engines."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from engines.alm.cashflow import VERSION as CASHFLOW_VERSION, compute_cashflow_buckets
from engines.alm.gap import VERSION as GAP_VERSION, compute_liquidity_gap
from engines.common.models import CashflowInput, CashflowItem


def _cf(cid: str, days_from_reporting: int, amount: Decimal,
        reporting_date: date = date(2024, 3, 31)) -> CashflowItem:
    return CashflowItem(
        cashflow_id=cid,
        position_id=f"pos_{cid}",
        cashflow_type="principal",
        cashflow_date=reporting_date + timedelta(days=days_from_reporting),
        amount=amount,
        currency="INR",
    )


def _input(*cashflows: CashflowItem, reporting_date: date = date(2024, 3, 31)) -> CashflowInput:
    return CashflowInput(
        snapshot_id="s",
        entity_id="e",
        reporting_date=reporting_date,
        cashflows=list(cashflows),
        currency="INR",
    )


class TestCashflowBucketAssignment:
    def test_day_1_goes_to_0_1d(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 1, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "0_1d")
        assert b.inflows == Decimal("100.00000000")

    def test_day_7_goes_to_1_7d(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 7, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "1_7d")
        assert b.inflows == Decimal("100.00000000")

    def test_day_8_goes_to_7_14d(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 8, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "7_14d")
        assert b.inflows == Decimal("100.00000000")

    def test_day_14_goes_to_7_14d(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 14, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "7_14d")
        assert b.inflows == Decimal("100.00000000")

    def test_day_28_goes_to_14_28d(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 28, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "14_28d")
        assert b.inflows == Decimal("100.00000000")

    def test_day_92_goes_to_28d_3m(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 92, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "28d_3m")
        assert b.inflows == Decimal("100.00000000")

    def test_day_183_goes_to_3m_6m(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 183, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "3m_6m")
        assert b.inflows == Decimal("100.00000000")

    def test_day_365_goes_to_6m_1y(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 365, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "6m_1y")
        assert b.inflows == Decimal("100.00000000")

    def test_day_1095_goes_to_1y_3y(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 1095, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "1y_3y")
        assert b.inflows == Decimal("100.00000000")

    def test_day_1826_goes_to_3y_5y(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 1826, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "3y_5y")
        assert b.inflows == Decimal("100.00000000")

    def test_day_1827_goes_to_gt_5y(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 1827, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "gt_5y")
        assert b.inflows == Decimal("100.00000000")

    def test_past_due_cashflow_goes_to_0_1d(self):
        # Negative days → treated as 0 days → 0_1d
        inp = CashflowInput(
            snapshot_id="s",
            entity_id="e",
            reporting_date=date(2024, 3, 31),
            cashflows=[
                CashflowItem(
                    cashflow_id="past",
                    position_id="pos_past",
                    cashflow_type="principal",
                    cashflow_date=date(2024, 3, 30),  # 1 day before reporting
                    amount=Decimal("100"),
                    currency="INR",
                )
            ],
            currency="INR",
        )
        result = compute_cashflow_buckets(inp).result
        b = next(b for b in result.buckets if b.time_bucket == "0_1d")
        assert b.inflows == Decimal("100.00000000")


class TestCashflowSignConvention:
    def test_positive_amount_is_inflow(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 1, Decimal("50")))).result
        assert result.total_inflows == Decimal("50.00000000")
        assert result.total_outflows == Decimal("0.00000000")

    def test_negative_amount_is_outflow(self):
        result = compute_cashflow_buckets(_input(_cf("c1", 1, Decimal("-50")))).result
        assert result.total_outflows == Decimal("50.00000000")
        assert result.total_inflows == Decimal("0.00000000")

    def test_net_per_bucket(self):
        # Same bucket: +100 inflow and -60 outflow → net = +40
        result = compute_cashflow_buckets(_input(
            _cf("in", 1, Decimal("100")),
            _cf("out", 1, Decimal("-60")),
        )).result
        b = next(b for b in result.buckets if b.time_bucket == "0_1d")
        assert b.net == Decimal("40.00000000")


class TestCashflowCumulative:
    def test_cumulative_net_is_rolling_sum(self):
        result = compute_cashflow_buckets(_input(
            _cf("a", 1, Decimal("100")),    # 0_1d  → net +100
            _cf("b", 7, Decimal("-30")),    # 1_7d  → net -30
            _cf("c", 14, Decimal("20")),    # 7_14d → net +20
        )).result
        buckets = {b.time_bucket: b for b in result.buckets}
        assert buckets["0_1d"].cumulative_net == Decimal("100.00000000")
        assert buckets["1_7d"].cumulative_net == Decimal("70.00000000")
        assert buckets["7_14d"].cumulative_net == Decimal("90.00000000")


class TestCashflowDeterminism:
    def test_same_inputs_identical_hashes(self):
        inp = _input(_cf("c1", 7, Decimal("100")), _cf("c2", 30, Decimal("-50")))
        r1 = compute_cashflow_buckets(inp)
        r2 = compute_cashflow_buckets(inp)
        assert r1.trace.inputs_hash == r2.trace.inputs_hash
        assert r1.trace.outputs_hash == r2.trace.outputs_hash

    def test_version_constant(self):
        assert CASHFLOW_VERSION == "1.0.0"


class TestLiquidityGap:
    def test_gap_is_inflows_minus_outflows(self):
        cf_result = compute_cashflow_buckets(_input(
            _cf("in", 1, Decimal("100")),
            _cf("out", 1, Decimal("-60")),
        )).result
        gap_result = compute_liquidity_gap(cf_result, total_assets=Decimal("1000")).result
        b = next(b for b in gap_result.buckets if b.time_bucket == "0_1d")
        assert b.gap == Decimal("40.00000000")

    def test_gap_ratio_is_cumulative_gap_over_total_assets_pct(self):
        cf_result = compute_cashflow_buckets(_input(
            _cf("in", 1, Decimal("100")),
        )).result
        gap_result = compute_liquidity_gap(cf_result, total_assets=Decimal("1000")).result
        b = next(b for b in gap_result.buckets if b.time_bucket == "0_1d")
        # cumulative_gap=100, total_assets=1000 → 10%
        assert b.gap_ratio_pct == Decimal("10.00000000")

    def test_negative_gap_is_funding_shortfall(self):
        cf_result = compute_cashflow_buckets(_input(
            _cf("out", 1, Decimal("-100")),
        )).result
        gap_result = compute_liquidity_gap(cf_result, total_assets=Decimal("1000")).result
        b = next(b for b in gap_result.buckets if b.time_bucket == "0_1d")
        assert b.gap < Decimal("0")

    def test_gap_version_constant(self):
        assert GAP_VERSION == "1.0.0"

    def test_gap_determinism(self):
        cf_result = compute_cashflow_buckets(_input(_cf("c1", 7, Decimal("200")))).result
        r1 = compute_liquidity_gap(cf_result, Decimal("1000"))
        r2 = compute_liquidity_gap(cf_result, Decimal("1000"))
        assert r1.trace.inputs_hash == r2.trace.inputs_hash
        assert r1.trace.outputs_hash == r2.trace.outputs_hash
