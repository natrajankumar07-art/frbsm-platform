"""
Unit tests for the SAM Planner base types (Epic 4D).
Tests: ExecutionPlan, ExecutionStep, PlanStatus, StepStatus, TimelineEvent.
"""

import pytest
from datetime import datetime, timezone

from app.services.ai.planner.base import (
    ExecutionPlan,
    ExecutionStep,
    PlanStatus,
    StepStatus,
    TimelineEvent,
    TimelineStage,
)


# ── StepStatus & PlanStatus enums ──────────────────────────────────────────

class TestStepStatus:
    def test_all_statuses_exist(self):
        for s in ("pending", "running", "completed", "failed", "skipped", "retrying"):
            assert StepStatus(s) is not None

    def test_status_is_string_enum(self):
        assert isinstance(StepStatus.PENDING, str)
        assert StepStatus.COMPLETED == "completed"


class TestPlanStatus:
    def test_all_statuses_exist(self):
        for s in ("draft", "executing", "completed", "failed", "partial"):
            assert PlanStatus(s) is not None

    def test_status_is_string_enum(self):
        assert isinstance(PlanStatus.COMPLETED, str)


# ── ExecutionStep ──────────────────────────────────────────────────────────

class TestExecutionStep:
    def _make_step(self) -> ExecutionStep:
        return ExecutionStep(
            step_id="abc12345",
            tool_name="list_entities",
            description="Discover entities",
        )

    def test_default_status_is_pending(self):
        step = self._make_step()
        assert step.status == StepStatus.PENDING

    def test_default_retry_count_zero(self):
        step = self._make_step()
        assert step.retry_count == 0

    def test_mark_running_sets_status_and_start_time(self):
        step = self._make_step()
        step.mark_running()
        assert step.status == StepStatus.RUNNING
        assert step.start_time is not None

    def test_mark_completed_sets_status_and_result(self):
        step = self._make_step()
        step.mark_running()
        step.mark_completed(result={"count": 3})
        assert step.status == StepStatus.COMPLETED
        assert step.result == {"count": 3}
        assert step.end_time is not None

    def test_mark_completed_calculates_duration(self):
        step = self._make_step()
        step.mark_running()
        step.mark_completed(result={})
        assert step.duration_ms is not None
        assert step.duration_ms >= 0

    def test_mark_failed_sets_error(self):
        step = self._make_step()
        step.mark_running()
        step.mark_failed("Something broke")
        assert step.status == StepStatus.FAILED
        assert step.error == "Something broke"
        assert step.end_time is not None

    def test_mark_skipped_sets_reason(self):
        step = self._make_step()
        step.mark_skipped("dependency failed")
        assert step.status == StepStatus.SKIPPED
        assert "dependency" in (step.error or "")

    def test_to_dict_has_required_keys(self):
        step = self._make_step()
        d = step.to_dict()
        for key in ("step_id", "tool_name", "description", "status", "depends_on",
                    "start_time", "end_time", "duration_ms", "retry_count", "error", "evidence"):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_status_is_string(self):
        step = self._make_step()
        d = step.to_dict()
        assert isinstance(d["status"], str)


# ── ExecutionPlan ──────────────────────────────────────────────────────────

class TestExecutionPlan:
    def _make_plan(self) -> ExecutionPlan:
        steps = [
            ExecutionStep(step_id="s1", tool_name="list_entities", description="Discover"),
            ExecutionStep(step_id="s2", tool_name="get_snapshots", description="Snapshots", depends_on=["s1"]),
        ]
        return ExecutionPlan.create(intent="Analyze LCR", steps=steps)

    def test_create_generates_plan_id(self):
        plan = self._make_plan()
        assert plan.plan_id and len(plan.plan_id) == 36  # UUID format

    def test_create_sets_draft_status(self):
        plan = self._make_plan()
        assert plan.status == PlanStatus.DRAFT

    def test_pending_steps_returns_all_on_new_plan(self):
        plan = self._make_plan()
        assert len(plan.pending_steps()) == 2

    def test_completed_steps_initially_empty(self):
        plan = self._make_plan()
        assert plan.completed_steps() == []

    def test_failed_steps_initially_empty(self):
        plan = self._make_plan()
        assert plan.failed_steps() == []

    def test_is_complete_false_initially(self):
        plan = self._make_plan()
        assert not plan.is_complete()

    def test_is_complete_true_when_all_done(self):
        plan = self._make_plan()
        for step in plan.steps:
            step.mark_running()
            step.mark_completed(result={})
        assert plan.is_complete()

    def test_is_complete_true_when_all_skipped(self):
        plan = self._make_plan()
        for step in plan.steps:
            step.mark_skipped()
        assert plan.is_complete()

    def test_has_failures_when_step_fails(self):
        plan = self._make_plan()
        plan.steps[0].mark_running()
        plan.steps[0].mark_failed("error")
        assert plan.has_failures()

    def test_get_step_by_id(self):
        plan = self._make_plan()
        s = plan.get_step("s1")
        assert s is not None
        assert s.tool_name == "list_entities"

    def test_get_step_unknown_returns_none(self):
        plan = self._make_plan()
        assert plan.get_step("nonexistent") is None

    def test_dependencies_met_no_deps(self):
        plan = self._make_plan()
        assert plan.dependencies_met(plan.steps[0])

    def test_dependencies_not_met_when_dep_pending(self):
        plan = self._make_plan()
        assert not plan.dependencies_met(plan.steps[1])

    def test_dependencies_met_after_dep_completes(self):
        plan = self._make_plan()
        plan.steps[0].mark_running()
        plan.steps[0].mark_completed(result={})
        assert plan.dependencies_met(plan.steps[1])

    def test_to_dict_has_required_keys(self):
        plan = self._make_plan()
        d = plan.to_dict()
        for key in ("plan_id", "intent", "status", "steps", "steps_total",
                    "steps_completed", "steps_failed", "steps_skipped", "created_at"):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_step_counts(self):
        plan = self._make_plan()
        d = plan.to_dict()
        assert d["steps_total"] == 2
        assert d["steps_completed"] == 0
        assert d["steps_failed"] == 0


# ── TimelineStage & TimelineEvent ──────────────────────────────────────────

class TestTimelineStage:
    def test_all_stages_have_labels(self):
        for stage in TimelineStage:
            assert isinstance(stage.label, str)
            assert len(stage.label) > 3

    def test_seven_stages(self):
        assert len(list(TimelineStage)) == 7

    def test_stage_values(self):
        expected = {"intent", "planning", "tool_calls", "evidence_collection",
                    "reasoning", "report_generation", "final_answer"}
        assert {s.value for s in TimelineStage} == expected


class TestTimelineEvent:
    def test_to_dict_has_required_keys(self):
        event = TimelineEvent(
            stage="intent",
            label="Intent Analysis",
            detail="Analyze LCR",
            timestamp="2026-07-01T00:00:00Z",
            status="completed",
        )
        d = event.to_dict()
        for key in ("stage", "label", "detail", "timestamp", "status"):
            assert key in d
