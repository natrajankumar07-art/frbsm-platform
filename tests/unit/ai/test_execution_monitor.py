"""
Unit tests for the SAM Execution Monitor (Epic 4D).
Tests: ExecutionRecord, StepRecord, ExecutionMonitor.
"""

import pytest

from app.services.ai.execution_monitor import (
    ExecutionMonitor,
    ExecutionRecord,
    StepRecord,
    get_monitor,
)
from app.services.ai.planner.base import ExecutionPlan, ExecutionStep, PlanStatus, StepStatus


# ── StepRecord ─────────────────────────────────────────────────────────────

class TestStepRecord:
    def _make(self) -> StepRecord:
        return StepRecord(
            step_id="abc",
            tool_name="list_entities",
            description="Discover entities",
            status="completed",
            start_time="2026-07-01T00:00:00Z",
            end_time="2026-07-01T00:00:01Z",
            duration_ms=1000,
            retry_count=0,
            error=None,
            evidence_confidence="HIGH",
        )

    def test_to_dict_has_required_keys(self):
        r = self._make()
        d = r.to_dict()
        for key in ("step_id", "tool_name", "description", "status",
                    "duration_ms", "retry_count", "error", "evidence_confidence"):
            assert key in d

    def test_confidence_preserved(self):
        r = self._make()
        assert r.to_dict()["evidence_confidence"] == "HIGH"


# ── ExecutionRecord ────────────────────────────────────────────────────────

class TestExecutionRecord:
    def _make(self) -> ExecutionRecord:
        return ExecutionRecord(
            execution_id="exec-001",
            plan_id="plan-001",
            intent="Analyze LCR",
            entity_id="entity-001",
            snapshot_id="snap-001",
            status="completed",
            steps=[],
            steps_completed=2,
            steps_failed=0,
            steps_skipped=0,
        )

    def test_to_dict_has_required_keys(self):
        r = self._make()
        d = r.to_dict()
        for key in ("execution_id", "plan_id", "intent", "status",
                    "steps_completed", "steps_failed", "steps_skipped"):
            assert key in d

    def test_steps_empty_by_default(self):
        r = self._make()
        assert r.steps == []


# ── ExecutionMonitor ───────────────────────────────────────────────────────

class TestExecutionMonitor:
    def _monitor(self) -> ExecutionMonitor:
        return ExecutionMonitor()

    def _record(self, idx: int = 0) -> ExecutionRecord:
        return ExecutionRecord(
            execution_id=f"exec-{idx:03d}",
            plan_id=f"plan-{idx:03d}",
            intent=f"Intent {idx}",
            entity_id=None,
            snapshot_id=None,
            status="completed",
            steps_completed=1,
            steps_failed=0,
            steps_skipped=0,
        )

    def test_initially_empty(self):
        m = self._monitor()
        assert m.get_history() == []

    def test_record_and_retrieve(self):
        m = self._monitor()
        r = self._record(1)
        m.record_execution(r)
        assert m.get_execution("exec-001") is not None

    def test_get_unknown_returns_none(self):
        m = self._monitor()
        assert m.get_execution("does-not-exist") is None

    def test_history_most_recent_first(self):
        m = self._monitor()
        m.record_execution(self._record(1))
        m.record_execution(self._record(2))
        history = m.get_history()
        assert history[0].execution_id == "exec-002"

    def test_history_limit_respected(self):
        m = self._monitor()
        for i in range(10):
            m.record_execution(self._record(i))
        assert len(m.get_history(limit=5)) == 5

    def test_capacity_evicts_oldest(self):
        m = self._monitor()
        m.MAX_HISTORY = 3  # Override for test
        for i in range(5):
            m.record_execution(self._record(i))
        # Oldest should be evicted
        assert m.get_execution("exec-000") is None
        assert m.get_execution("exec-004") is not None

    def test_record_from_plan(self):
        m = self._monitor()
        steps = [
            ExecutionStep(step_id="s1", tool_name="list_entities", description="Find"),
        ]
        steps[0].mark_running()
        steps[0].mark_completed(result={}, evidence={"confidence": "HIGH"})
        plan = ExecutionPlan.create(intent="Test", steps=steps)
        plan.status = PlanStatus.COMPLETED
        plan.completed_at = "2026-07-01T00:00:02Z"

        record = m.record_from_plan(plan)
        assert record.plan_id == plan.plan_id
        assert record.steps_completed == 1
        assert record.steps_failed == 0

    def test_record_from_plan_captures_evidence_confidence(self):
        m = self._monitor()
        step = ExecutionStep(step_id="s1", tool_name="list_entities", description="Find")
        step.mark_running()
        step.mark_completed(result={}, evidence={"confidence": "MEDIUM"})
        plan = ExecutionPlan.create(intent="Test", steps=[step])
        plan.status = PlanStatus.COMPLETED

        record = m.record_from_plan(plan)
        assert record.steps[0].evidence_confidence == "MEDIUM"


# ── Module-level singleton ─────────────────────────────────────────────────

class TestGetMonitor:
    def test_returns_execution_monitor_instance(self):
        m = get_monitor()
        assert isinstance(m, ExecutionMonitor)

    def test_singleton_same_object(self):
        m1 = get_monitor()
        m2 = get_monitor()
        assert m1 is m2
