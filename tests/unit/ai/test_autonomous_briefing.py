"""
Unit tests for the autonomous briefing generator (Epic 6).
Tests: BriefingType, BriefingKeyMetrics, BriefingInput, generate_briefing.
No DB required.
"""

import pytest

from app.services.ai.autonomous.briefing import (
    BriefingInput,
    BriefingKeyMetrics,
    BriefingType,
    generate_briefing,
)


class TestBriefingType:
    def test_all_types_exist(self):
        for t in ("morning", "daily", "weekly", "monthly_board", "quarterly_exec"):
            assert BriefingType(t) is not None

    def test_labels_are_strings(self):
        for t in BriefingType:
            assert isinstance(t.label, str)
            assert len(t.label) > 0


class TestBriefingKeyMetrics:
    def test_to_dict_returns_dict(self):
        m = BriefingKeyMetrics(lcr_ratio=1.25, nsfr_ratio=1.1, cet1_ratio=0.12)
        d = m.to_dict()
        assert isinstance(d, dict)
        assert d["lcr_ratio"] == 1.25
        assert d["nsfr_ratio"] == 1.1
        assert d["cet1_ratio"] == 0.12

    def test_to_dict_all_none(self):
        m = BriefingKeyMetrics()
        d = m.to_dict()
        assert d["lcr_ratio"] is None
        assert d["currency"] == "USD"


class TestGenerateBriefing:
    def _make_input(self, **overrides):
        km = BriefingKeyMetrics(lcr_ratio=1.25, nsfr_ratio=1.1, cet1_ratio=0.12,
                                tier1_ratio=0.14, total_capital_ratio=0.16, leverage_ratio=0.05)
        base = dict(
            entity_name="Test Bank",
            briefing_type="morning",
            metrics=km,
            alert_count=0,
            critical_alert_count=0,
            warning_alert_count=0,
            open_issue_count=0,
        )
        base.update(overrides)
        return BriefingInput(**base)

    def test_returns_string(self):
        result = generate_briefing(self._make_input())
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_entity_name(self):
        result = generate_briefing(self._make_input())
        assert "Test Bank" in result

    def test_contains_executive_summary_section(self):
        result = generate_briefing(self._make_input())
        assert "Executive Summary" in result

    def test_contains_key_metrics_table(self):
        result = generate_briefing(self._make_input())
        assert "Key Metrics" in result
        assert "LCR" in result
        assert "NSFR" in result

    def test_contains_regulatory_status(self):
        result = generate_briefing(self._make_input())
        assert "Regulatory Status" in result

    def test_contains_recommended_actions(self):
        result = generate_briefing(self._make_input())
        assert "Recommended Actions" in result

    def test_all_pass_shows_compliant(self):
        result = generate_briefing(self._make_input())
        assert "Compliant" in result

    def test_lcr_breach_shows_noncompliant(self):
        km = BriefingKeyMetrics(lcr_ratio=0.85, nsfr_ratio=1.1, cet1_ratio=0.12)
        result = generate_briefing(self._make_input(metrics=km))
        assert "Non-Compliant" in result or "Breach" in result

    def test_alert_count_shown_when_present(self):
        result = generate_briefing(self._make_input(alert_count=3, critical_alert_count=1, warning_alert_count=2))
        assert "3 active alert" in result

    def test_top_alerts_included(self):
        inp = self._make_input(
            alert_count=1,
            top_alerts=[{"severity": "critical", "title": "LCR Breach", "message": "LCR below 100%"}]
        )
        result = generate_briefing(inp)
        assert "LCR Breach" in result

    def test_top_recommendations_included(self):
        inp = self._make_input(
            top_recommendations=[{
                "priority": 1,
                "title": "Increase HQLA",
                "description": "Acquire additional HQLAs",
                "category": "liquidity",
            }]
        )
        result = generate_briefing(inp)
        assert "Increase HQLA" in result

    def test_none_metrics_handled(self):
        km = BriefingKeyMetrics()
        result = generate_briefing(self._make_input(metrics=km))
        assert isinstance(result, str)
        assert "—" in result  # placeholder for None values

    def test_all_briefing_types_generate(self):
        for bt in BriefingType:
            inp = self._make_input(briefing_type=bt.value)
            result = generate_briefing(inp)
            assert bt.label in result

    def test_sam_disclaimer_present(self):
        result = generate_briefing(self._make_input())
        assert "SAM does not compute regulatory ratios" in result
