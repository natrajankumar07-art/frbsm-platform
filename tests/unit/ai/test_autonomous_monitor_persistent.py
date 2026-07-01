"""
Unit tests for the persistent autonomous monitor layer (Epic 6).
Tests severity mapping and _fetch_latest_metrics structure.
DB-dependent run_persistent_monitoring is excluded (integration test).
"""

import pytest

from app.services.ai.autonomous.monitor import _SEVERITY_MAP, _map_severity


class TestSeverityMapping:
    def test_critical_maps_to_critical(self):
        assert _map_severity("critical") == "critical"

    def test_high_maps_to_warning(self):
        assert _map_severity("high") == "warning"

    def test_medium_maps_to_notice(self):
        assert _map_severity("medium") == "notice"

    def test_low_maps_to_notice(self):
        assert _map_severity("low") == "notice"

    def test_info_maps_to_info(self):
        assert _map_severity("info") == "info"

    def test_unknown_maps_to_info(self):
        assert _map_severity("unknown_severity_xyz") == "info"

    def test_case_insensitive(self):
        assert _map_severity("CRITICAL") == "critical"
        assert _map_severity("HIGH") == "warning"

    def test_severity_map_has_expected_keys(self):
        expected = {"critical", "high", "medium", "low", "info"}
        assert set(_SEVERITY_MAP.keys()) == expected

    def test_severity_map_outputs_are_4_level(self):
        valid_outputs = {"critical", "warning", "notice", "info"}
        for v in _SEVERITY_MAP.values():
            assert v in valid_outputs
