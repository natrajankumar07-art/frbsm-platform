"""
Unit tests for autonomous trend detection (Epic 6).
Tests: TrendDirection enum, TrendResult, detect_trend, classify_metric_trend.
"""

import pytest

from app.services.ai.autonomous.trend import (
    TrendDirection,
    TrendResult,
    classify_metric_trend,
    detect_trend,
)


class TestTrendDirection:
    def test_all_directions_exist(self):
        for d in ("IMPROVING", "STABLE", "DETERIORATING", "RAPID_CHANGE"):
            assert TrendDirection[d] is not None

    def test_values_are_strings(self):
        assert isinstance(TrendDirection.IMPROVING.value, str)


class TestDetectTrend:
    def test_empty_list_returns_stable(self):
        result = detect_trend([])
        assert result.direction == TrendDirection.STABLE

    def test_single_value_returns_stable(self):
        result = detect_trend([1.2])
        assert result.direction == TrendDirection.STABLE

    def test_two_identical_values_stable(self):
        result = detect_trend([1.1, 1.1])
        assert result.direction == TrendDirection.STABLE

    def test_improving_trend(self):
        # +10% change → IMPROVING
        result = detect_trend([1.0, 1.1])
        assert result.direction == TrendDirection.IMPROVING

    def test_deteriorating_trend(self):
        # -10% change → DETERIORATING
        result = detect_trend([1.1, 1.0])
        assert result.direction == TrendDirection.DETERIORATING

    def test_rapid_increase(self):
        # +25% change → RAPID_CHANGE
        result = detect_trend([1.0, 1.25])
        assert result.direction == TrendDirection.RAPID_CHANGE

    def test_rapid_decrease(self):
        # -25% change → RAPID_CHANGE
        result = detect_trend([1.25, 1.0])
        assert result.direction == TrendDirection.RAPID_CHANGE

    def test_small_change_stable(self):
        # +2% → STABLE (within ±5%)
        result = detect_trend([1.0, 1.02])
        assert result.direction == TrendDirection.STABLE

    def test_pct_change_calculated(self):
        result = detect_trend([1.0, 1.1])
        assert abs(result.pct_change - 10.0) < 0.01

    def test_result_has_explanation(self):
        result = detect_trend([1.0, 1.1])
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 0

    def test_result_values_recorded(self):
        result = detect_trend([1.0, 1.2])
        assert result.previous_value == 1.0
        assert result.latest_value == 1.2

    def test_longer_series_uses_first_and_last(self):
        # First: 1.0, Last: 1.15 → +15% → IMPROVING
        result = detect_trend([1.0, 1.05, 1.08, 1.15])
        assert result.direction == TrendDirection.IMPROVING


class TestClassifyMetricTrend:
    def test_lcr_improving_message(self):
        trend = detect_trend([1.0, 1.1])
        msg = classify_metric_trend("lcr", trend)
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_cet1_deteriorating_message(self):
        trend = detect_trend([0.12, 0.10])
        msg = classify_metric_trend("cet1", trend)
        assert isinstance(msg, str)

    def test_unknown_metric_returns_generic(self):
        trend = detect_trend([1.0, 1.05])
        msg = classify_metric_trend("unknown_metric_xyz", trend)
        assert isinstance(msg, str)
