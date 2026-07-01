"""
Unit tests for the SAM Autonomous Monitor (Epic 4D).
Tests: Alert, AlertSeverity, AlertCategory, threshold constants.
(DB-dependent check functions are excluded from unit tests — they run in integration tests.)
"""

import pytest

from app.services.ai.autonomous_monitor import (
    Alert,
    AlertCategory,
    AlertSeverity,
    CET1_MIN_RATIO,
    CET1_WARNING_RATIO,
    LCR_MIN_RATIO,
    LCR_WARNING_RATIO,
    NSFR_MIN_RATIO,
    NSFR_WARNING_RATIO,
    T1_MIN_RATIO,
    TCR_MIN_RATIO,
    _alert,
)


# ── AlertSeverity & AlertCategory ──────────────────────────────────────────

class TestAlertSeverity:
    def test_all_severities_exist(self):
        for s in ("critical", "high", "medium", "low", "info"):
            assert AlertSeverity(s) is not None

    def test_is_string_enum(self):
        assert isinstance(AlertSeverity.CRITICAL, str)
        assert AlertSeverity.CRITICAL == "critical"


class TestAlertCategory:
    def test_all_categories_exist(self):
        for c in ("lcr", "nsfr", "capital", "workflow", "data", "system"):
            assert AlertCategory(c) is not None


# ── Thresholds ─────────────────────────────────────────────────────────────

class TestThresholds:
    def test_lcr_minimum_is_one(self):
        assert LCR_MIN_RATIO == 1.0

    def test_nsfr_minimum_is_one(self):
        assert NSFR_MIN_RATIO == 1.0

    def test_lcr_warning_above_minimum(self):
        assert LCR_WARNING_RATIO > LCR_MIN_RATIO

    def test_nsfr_warning_above_minimum(self):
        assert NSFR_WARNING_RATIO > NSFR_MIN_RATIO

    def test_cet1_minimum_is_4_5_percent(self):
        assert CET1_MIN_RATIO == 4.5

    def test_t1_minimum_is_6_percent(self):
        assert T1_MIN_RATIO == 6.0

    def test_tcr_minimum_is_8_percent(self):
        assert TCR_MIN_RATIO == 8.0

    def test_cet1_warning_above_minimum(self):
        assert CET1_WARNING_RATIO > CET1_MIN_RATIO


# ── Alert dataclass ────────────────────────────────────────────────────────

class TestAlert:
    def _make(self) -> Alert:
        return _alert(
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.LCR,
            title="LCR Breach — Test Bank",
            message="LCR ratio 0.85 is below minimum 1.0",
            entity="Test Bank",
            snapshot_date="2026-03-31",
            metric_name="lcr_ratio",
            metric_value=0.85,
            threshold=1.0,
        )

    def test_alert_has_alert_id(self):
        a = self._make()
        assert a.alert_id and len(a.alert_id) > 0

    def test_severity_is_string(self):
        a = self._make()
        assert isinstance(a.severity, str)
        assert a.severity == "critical"

    def test_to_dict_has_required_keys(self):
        a = self._make()
        d = a.to_dict()
        for key in ("alert_id", "severity", "category", "title", "message",
                    "entity", "snapshot_date", "metric_name", "metric_value",
                    "threshold", "generated_at"):
            assert key in d, f"Missing key: {key}"

    def test_metric_value_preserved(self):
        a = self._make()
        d = a.to_dict()
        assert d["metric_value"] == pytest.approx(0.85)

    def test_threshold_preserved(self):
        a = self._make()
        assert a.threshold == pytest.approx(1.0)

    def test_generated_at_is_iso_string(self):
        a = self._make()
        assert "T" in a.generated_at  # ISO 8601 format

    def test_high_severity_alert(self):
        a = _alert(
            severity=AlertSeverity.HIGH,
            category=AlertCategory.NSFR,
            title="NSFR Warning",
            message="NSFR near minimum",
            entity="Bank",
            snapshot_date="2026-03-31",
        )
        assert a.severity == "high"
        assert a.category == "nsfr"

    def test_medium_severity_capital_alert(self):
        a = _alert(
            severity=AlertSeverity.MEDIUM,
            category=AlertCategory.CAPITAL,
            title="CET1 Watch",
            message="CET1 below warning threshold",
            entity="Bank",
            snapshot_date="2026-03-31",
            metric_name="cet1_ratio",
            metric_value=5.5,
            threshold=6.0,
        )
        assert a.severity == "medium"
        assert a.to_dict()["metric_value"] == pytest.approx(5.5)
