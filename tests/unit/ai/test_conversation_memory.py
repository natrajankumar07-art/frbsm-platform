"""
Unit tests for Epic 4C conversation memory.
"""

import json
from datetime import datetime

import pytest

from app.services.ai.memory import SessionMemory

ENTITY_ID = "a1000000-0000-0000-0000-000000000001"
ENTITY_NAME = "BSM Demo Bank Ltd"
SNAP_ID = "d1000000-0000-0000-0000-000000000001"
SNAP_DATE = "2026-03-31"


# ── SessionMemory dataclass ────────────────────────────────────────────────

class TestSessionMemory:
    def test_default_state_is_empty(self):
        m = SessionMemory()
        assert m.active_entity_id is None
        assert m.active_snapshot_id is None
        assert m.active_entity_name is None
        assert m.active_snapshot_date is None
        assert m.recent_snapshot_ids == []
        assert m.recent_entity_ids == []
        assert m.report_history == []
        assert m.last_tool_calls == []

    def test_set_active_entity(self):
        m = SessionMemory()
        m.set_active_entity(ENTITY_ID, ENTITY_NAME)
        assert m.active_entity_id == ENTITY_ID
        assert m.active_entity_name == ENTITY_NAME

    def test_set_active_entity_adds_to_recent(self):
        m = SessionMemory()
        m.set_active_entity(ENTITY_ID, ENTITY_NAME)
        assert ENTITY_ID in m.recent_entity_ids

    def test_set_active_entity_no_duplicate_in_recent(self):
        m = SessionMemory()
        m.set_active_entity(ENTITY_ID, ENTITY_NAME)
        m.set_active_entity(ENTITY_ID, ENTITY_NAME)
        assert m.recent_entity_ids.count(ENTITY_ID) == 1

    def test_set_active_snapshot(self):
        m = SessionMemory()
        m.set_active_snapshot(SNAP_ID, SNAP_DATE)
        assert m.active_snapshot_id == SNAP_ID
        assert m.active_snapshot_date == SNAP_DATE

    def test_set_active_snapshot_adds_to_recent(self):
        m = SessionMemory()
        m.set_active_snapshot(SNAP_ID, SNAP_DATE)
        assert SNAP_ID in m.recent_snapshot_ids

    def test_recent_list_capped_at_five(self):
        m = SessionMemory()
        for i in range(10):
            m.set_active_entity(f"entity-{i}", f"Entity {i}")
        assert len(m.recent_entity_ids) <= 5

    def test_record_tool_call(self):
        m = SessionMemory()
        m.record_tool_call("list_entities", "Found 3 entities")
        assert len(m.last_tool_calls) == 1
        assert m.last_tool_calls[0]["tool"] == "list_entities"

    def test_record_tool_call_has_timestamp(self):
        m = SessionMemory()
        m.record_tool_call("get_snapshots", "Found 2 snapshots")
        assert "timestamp" in m.last_tool_calls[0]

    def test_record_tool_call_summary_truncated(self):
        m = SessionMemory()
        long_summary = "x" * 500
        m.record_tool_call("test", long_summary)
        assert len(m.last_tool_calls[0]["summary"]) <= 200

    def test_tool_calls_capped_at_ten(self):
        m = SessionMemory()
        for i in range(15):
            m.record_tool_call(f"tool_{i}", "summary")
        assert len(m.last_tool_calls) <= 10

    def test_tool_calls_most_recent_first(self):
        m = SessionMemory()
        m.record_tool_call("first_tool", "first")
        m.record_tool_call("second_tool", "second")
        assert m.last_tool_calls[0]["tool"] == "second_tool"

    def test_record_report(self):
        m = SessionMemory()
        m.record_report("executive_dashboard")
        assert len(m.report_history) == 1
        assert m.report_history[0]["report_type"] == "executive_dashboard"

    def test_report_history_has_generated_at(self):
        m = SessionMemory()
        m.record_report("ceo_brief")
        assert "generated_at" in m.report_history[0]

    def test_report_history_capped_at_five(self):
        m = SessionMemory()
        for rt in ["a", "b", "c", "d", "e", "f", "g"]:
            m.record_report(rt)
        assert len(m.report_history) <= 5

    def test_report_history_most_recent_first(self):
        m = SessionMemory()
        m.record_report("first_report")
        m.record_report("second_report")
        assert m.report_history[0]["report_type"] == "second_report"


# ── Serialisation round-trip ───────────────────────────────────────────────

class TestSessionMemorySerialization:
    def _populated_memory(self) -> SessionMemory:
        m = SessionMemory()
        m.set_active_entity(ENTITY_ID, ENTITY_NAME)
        m.set_active_snapshot(SNAP_ID, SNAP_DATE)
        m.record_tool_call("list_entities", "Found 1 entity")
        m.record_report("executive_dashboard")
        return m

    def test_to_dict_roundtrip(self):
        m = self._populated_memory()
        d = m.to_dict()
        m2 = SessionMemory.from_dict(d)
        assert m2.active_entity_id == ENTITY_ID
        assert m2.active_entity_name == ENTITY_NAME
        assert m2.active_snapshot_id == SNAP_ID
        assert m2.active_snapshot_date == SNAP_DATE

    def test_to_dict_is_json_serializable(self):
        m = self._populated_memory()
        d = m.to_dict()
        serialized = json.dumps(d)
        assert isinstance(serialized, str)
        assert len(serialized) > 10

    def test_from_dict_empty_dict_returns_default(self):
        m = SessionMemory.from_dict({})
        assert m.active_entity_id is None
        assert m.last_tool_calls == []

    def test_from_dict_with_extra_keys_is_safe(self):
        d = {"active_entity_id": ENTITY_ID, "unknown_key": "ignored"}
        m = SessionMemory.from_dict(d)
        assert m.active_entity_id == ENTITY_ID


# ── Context preamble ───────────────────────────────────────────────────────

class TestContextPreamble:
    def test_empty_memory_returns_empty_string(self):
        m = SessionMemory()
        assert m.build_context_preamble() == ""

    def test_preamble_includes_entity_name(self):
        m = SessionMemory()
        m.set_active_entity(ENTITY_ID, ENTITY_NAME)
        m.set_active_snapshot(SNAP_ID, SNAP_DATE)
        preamble = m.build_context_preamble()
        assert ENTITY_NAME in preamble

    def test_preamble_includes_snapshot_date(self):
        m = SessionMemory()
        m.set_active_entity(ENTITY_ID, ENTITY_NAME)
        m.set_active_snapshot(SNAP_ID, SNAP_DATE)
        preamble = m.build_context_preamble()
        assert SNAP_DATE in preamble

    def test_preamble_includes_last_tool(self):
        m = SessionMemory()
        m.set_active_entity(ENTITY_ID, ENTITY_NAME)
        m.set_active_snapshot(SNAP_ID, SNAP_DATE)
        m.record_tool_call("list_entities", "Found 3 entities")
        preamble = m.build_context_preamble()
        assert "list_entities" in preamble

    def test_preamble_is_string(self):
        m = SessionMemory()
        m.set_active_entity(ENTITY_ID, ENTITY_NAME)
        assert isinstance(m.build_context_preamble(), str)
