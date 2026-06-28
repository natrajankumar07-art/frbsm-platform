"""Unit tests for the Structural Liquidity Statement (SLS) engine."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from engines.common.models import CashflowInput, CashflowItem
from engines.liquidity.sls import VERSION, SLS_BUCKETS, compute_sls


def _cf(cid: str, days: int, amount: Decimal,
        reporting_date: date = date(2024, 3, 31)) -> CashflowItem:
    return CashflowItem(
        cashflow_id=cid,
        position_id=f"pos_{cid}",
        cashflow_type="principal",
        cashflow_date=reporting_date + timedelta(days=days),
        amount=amount,
        currency="INR",
    )


def _input(*cashflows: CashflowItem) -> CashflowInput:
    return CashflowInput(
        snapshot_id="s",
        entity_id="e",
        reporting_date=date(2024, 3, 31),
        cashflows=list(cashflows),
        currency="INR",
    )


class TestSLSBucketDefinition:
    def test_ten_buckets_defined(self):
        assert len(SLS_BUCKETS) == 10

    def test_bucket_names(self):
        names = [b[0] for b in SLS_BUCKETS]
        assert names == ["0_1d", "1_7d", "7_14d", "14_28d", "28d_3m", "3m_6m", "6m_1y", "1y_3y", "3y_5y", "gt_5y"]

    def test_result_has_ten_buckets(self):
        result = compute_sls(_input(_cf("c1", 1, Decimal("100")))).result
        assert len(result.buckets) == 10


class TestSLSBucketBoundaries:
    """Verify exact boundary placement (same logic as cashflow engine)."""

    def test_day_1_in_bucket_0_1d(self):
        result = compute_sls(_input(_cf("c1", 1, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "0_1d")
        assert b.total_inflows == Decimal("100.00000000")

    def test_day_7_in_bucket_1_7d(self):
        result = compute_sls(_input(_cf("c1", 7, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "1_7d")
        assert b.total_inflows == Decimal("100.00000000")

    def test_day_14_in_bucket_7_14d(self):
        result = compute_sls(_input(_cf("c1", 14, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "7_14d")
        assert b.total_inflows == Decimal("100.00000000")

    def test_day_28_in_bucket_14_28d(self):
        result = compute_sls(_input(_cf("c1", 28, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "14_28d")
        assert b.total_inflows == Decimal("100.00000000")

    def test_day_29_in_bucket_28d_3m(self):
        result = compute_sls(_input(_cf("c1", 29, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "28d_3m")
        assert b.total_inflows == Decimal("100.00000000")

    def test_day_93_in_bucket_3m_6m(self):
        result = compute_sls(_input(_cf("c1", 93, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "3m_6m")
        assert b.total_inflows == Decimal("100.00000000")

    def test_day_184_in_bucket_6m_1y(self):
        result = compute_sls(_input(_cf("c1", 184, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "6m_1y")
        assert b.total_inflows == Decimal("100.00000000")

    def test_day_366_in_bucket_1y_3y(self):
        result = compute_sls(_input(_cf("c1", 366, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "1y_3y")
        assert b.total_inflows == Decimal("100.00000000")

    def test_day_1096_in_bucket_3y_5y(self):
        result = compute_sls(_input(_cf("c1", 1096, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "3y_5y")
        assert b.total_inflows == Decimal("100.00000000")

    def test_day_2000_in_bucket_gt_5y(self):
        result = compute_sls(_input(_cf("c1", 2000, Decimal("100")))).result
        b = next(b for b in result.buckets if b.time_bucket == "gt_5y")
        assert b.total_inflows == Decimal("100.00000000")


class TestSLSNetAndCumulative:
    def test_net_position_inflow_minus_outflow(self):
        result = compute_sls(_input(
            _cf("in", 1, Decimal("100")),
            _cf("out", 1, Decimal("-40")),
        )).result
        b = next(b for b in result.buckets if b.time_bucket == "0_1d")
        assert b.net_position == Decimal("60.00000000")

    def test_cumulative_net_rolls_across_buckets(self):
        result = compute_sls(_input(
            _cf("a", 1, Decimal("100")),    # 0_1d net=+100
            _cf("b", 7, Decimal("-50")),    # 1_7d net=-50
            _cf("c", 14, Decimal("30")),    # 7_14d net=+30
        )).result
        buckets = {b.time_bucket: b for b in result.buckets}
        assert buckets["0_1d"].cumulative_net == Decimal("100.00000000")
        assert buckets["1_7d"].cumulative_net == Decimal("50.00000000")
        assert buckets["7_14d"].cumulative_net == Decimal("80.00000000")

    def test_total_inflows_and_outflows(self):
        result = compute_sls(_input(
            _cf("i1", 1, Decimal("100")),
            _cf("i2", 7, Decimal("50")),
            _cf("o1", 14, Decimal("-80")),
        )).result
        assert result.total_inflows == Decimal("150.00000000")
        assert result.total_outflows == Decimal("80.00000000")
        assert result.net_position == Decimal("70.00000000")

    def test_empty_buckets_have_zero_values(self):
        result = compute_sls(_input(_cf("c1", 1, Decimal("100")))).result
        empty = [b for b in result.buckets if b.time_bucket != "0_1d"]
        for b in empty:
            assert b.total_inflows == Decimal("0.00000000")
            assert b.total_outflows == Decimal("0.00000000")


class TestSLSDeterminism:
    def test_same_inputs_identical_hashes(self):
        inp = _input(_cf("c1", 7, Decimal("100")), _cf("c2", 30, Decimal("-50")))
        r1 = compute_sls(inp)
        r2 = compute_sls(inp)
        assert r1.trace.inputs_hash == r2.trace.inputs_hash
        assert r1.trace.outputs_hash == r2.trace.outputs_hash

    def test_version_constant(self):
        assert VERSION == "1.0.0"
