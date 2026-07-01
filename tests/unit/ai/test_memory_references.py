"""
Unit tests for SAM conversation reference resolution (Epic 4D).
Tests: SessionMemory.resolve_reference() for all reference types.
"""

import pytest

from app.services.ai.memory import SessionMemory

ENTITY_ID = "a1000000-0000-0000-0000-000000000001"
ENTITY_NAME = "BSM Demo Bank Ltd"
SNAP_ID_1 = "d1000000-0000-0000-0000-000000000001"
SNAP_ID_2 = "d2000000-0000-0000-0000-000000000002"
SNAP_DATE = "2026-03-31"


class TestResolveReference:
    def _memory_with_context(self) -> SessionMemory:
        m = SessionMemory()
        m.set_active_entity(ENTITY_ID, ENTITY_NAME)
        m.set_active_snapshot(SNAP_ID_1, SNAP_DATE)
        return m

    def test_none_reference_returns_empty_dict(self):
        m = self._memory_with_context()
        assert m.resolve_reference(None) == {}

    def test_active_entity_resolves_to_entity_id(self):
        m = self._memory_with_context()
        result = m.resolve_reference("active_entity")
        assert result["entity_id"] == ENTITY_ID

    def test_active_entity_resolves_to_entity_name(self):
        m = self._memory_with_context()
        result = m.resolve_reference("active_entity")
        assert result["entity_name"] == ENTITY_NAME

    def test_active_snapshot_resolves_to_snapshot_id(self):
        m = self._memory_with_context()
        result = m.resolve_reference("active_snapshot")
        assert result["snapshot_id"] == SNAP_ID_1

    def test_active_snapshot_resolves_to_snapshot_date(self):
        m = self._memory_with_context()
        result = m.resolve_reference("active_snapshot")
        assert result["snapshot_date"] == SNAP_DATE

    def test_previous_month_returns_second_recent_snapshot(self):
        m = SessionMemory()
        m.set_active_snapshot(SNAP_ID_1, "2026-03-31")
        m.set_active_snapshot(SNAP_ID_2, "2026-04-30")
        result = m.resolve_reference("previous_month")
        assert result.get("snapshot_id") == SNAP_ID_1

    def test_previous_month_falls_back_to_active_when_only_one(self):
        m = SessionMemory()
        m.set_active_snapshot(SNAP_ID_1, SNAP_DATE)
        result = m.resolve_reference("previous_month")
        assert result.get("snapshot_id") == SNAP_ID_1

    def test_previous_quarter_same_as_previous_month(self):
        m = SessionMemory()
        m.set_active_snapshot(SNAP_ID_1, "2026-03-31")
        m.set_active_snapshot(SNAP_ID_2, "2026-06-30")
        r1 = m.resolve_reference("previous_month")
        r2 = m.resolve_reference("previous_quarter")
        assert r1 == r2

    def test_repeat_analysis_returns_last_tool(self):
        m = self._memory_with_context()
        m.record_tool_call("list_entities", "Found 3 entities")
        result = m.resolve_reference("repeat_analysis")
        assert result.get("repeat_tool") == "list_entities"

    def test_repeat_analysis_empty_when_no_tool_calls(self):
        m = SessionMemory()
        result = m.resolve_reference("repeat_analysis")
        assert result == {}

    def test_repeat_report_returns_last_report_type(self):
        m = self._memory_with_context()
        m.record_report("executive_dashboard")
        result = m.resolve_reference("repeat_report")
        assert result.get("report_type") == "executive_dashboard"

    def test_repeat_report_empty_when_no_history(self):
        m = SessionMemory()
        result = m.resolve_reference("repeat_report")
        assert result == {}

    def test_unknown_reference_returns_empty_dict(self):
        m = self._memory_with_context()
        result = m.resolve_reference("completely_unknown_reference")
        assert result == {}

    def test_previous_period_resolves(self):
        m = SessionMemory()
        m.set_active_snapshot(SNAP_ID_1, SNAP_DATE)
        result = m.resolve_reference("previous_period")
        assert "snapshot_id" in result

    def test_previous_year_resolves(self):
        m = SessionMemory()
        m.set_active_snapshot(SNAP_ID_1, SNAP_DATE)
        result = m.resolve_reference("previous_year")
        assert "snapshot_id" in result
