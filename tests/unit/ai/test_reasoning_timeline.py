"""
Unit tests for the SAM Reasoning Timeline (Epic 4D).
Tests: build_timeline() produces correct 7-stage timeline events.
"""

import pytest

from app.services.ai.planner.base import (
    ExecutionPlan,
    ExecutionStep,
    PlanStatus,
    StepStatus,
    TimelineStage,
)
from app.services.ai.reasoning_timeline import build_timeline


def _make_plan(
    intent: str = "Analyze LCR for BSM Demo Bank",
    complete: bool = True,
) -> ExecutionPlan:
    steps = [
        ExecutionStep(step_id="s1", tool_name="list_entities", description="Discover entities"),
        ExecutionStep(step_id="s2", tool_name="get_snapshots", description="Get snapshots", depends_on=["s1"]),
        ExecutionStep(step_id="s3", tool_name="summarize_regulatory_results", description="Regulatory summary", depends_on=["s2"]),
    ]
    if complete:
        for step in steps:
            step.mark_running()
            step.mark_completed(result={}, evidence={"confidence": "HIGH"})
    plan = ExecutionPlan.create(intent=intent, steps=steps)
    if complete:
        plan.status = PlanStatus.COMPLETED
        plan.completed_at = "2026-07-01T00:00:05Z"
    return plan


class TestBuildTimeline:
    def test_returns_list_of_events(self):
        plan = _make_plan()
        events = build_timeline(plan)
        assert isinstance(events, list)
        assert len(events) > 0

    def test_first_event_is_intent(self):
        plan = _make_plan()
        events = build_timeline(plan)
        assert events[0].stage == TimelineStage.INTENT.value

    def test_second_event_is_planning(self):
        plan = _make_plan()
        events = build_timeline(plan)
        assert events[1].stage == TimelineStage.PLANNING.value

    def test_planning_mentions_step_count(self):
        plan = _make_plan()
        events = build_timeline(plan)
        planning_evt = next(e for e in events if e.stage == "planning")
        assert "3" in planning_evt.detail  # 3 steps

    def test_tool_calls_event_present_when_steps_ran(self):
        plan = _make_plan()
        events = build_timeline(plan)
        stages = [e.stage for e in events]
        assert TimelineStage.TOOL_CALLS.value in stages

    def test_evidence_collection_event_when_evidence_present(self):
        plan = _make_plan()
        events = build_timeline(plan)
        stages = [e.stage for e in events]
        assert TimelineStage.EVIDENCE_COLLECTION.value in stages

    def test_reasoning_event_present_on_completed_plan(self):
        plan = _make_plan()
        events = build_timeline(plan)
        stages = [e.stage for e in events]
        assert TimelineStage.REASONING.value in stages

    def test_final_answer_event_present(self):
        plan = _make_plan()
        events = build_timeline(plan)
        stages = [e.stage for e in events]
        assert TimelineStage.FINAL_ANSWER.value in stages

    def test_all_events_have_required_fields(self):
        plan = _make_plan()
        events = build_timeline(plan)
        for evt in events:
            assert evt.stage
            assert evt.label
            assert evt.detail
            assert evt.timestamp
            assert evt.status in ("completed", "running", "pending", "failed")

    def test_intent_detail_truncated_to_120_chars(self):
        long_intent = "A" * 200
        plan = _make_plan(intent=long_intent)
        events = build_timeline(plan)
        intent_evt = next(e for e in events if e.stage == "intent")
        assert len(intent_evt.detail) <= 120

    def test_failed_plan_produces_failed_final_answer(self):
        steps = [
            ExecutionStep(step_id="s1", tool_name="list_entities", description="Discover"),
        ]
        steps[0].mark_running()
        steps[0].mark_failed("DB error")
        plan = ExecutionPlan.create(intent="Analyze", steps=steps)
        plan.status = PlanStatus.FAILED
        plan.completed_at = "2026-07-01T00:00:05Z"

        events = build_timeline(plan)
        final = next((e for e in events if e.stage == "final_answer"), None)
        assert final is not None
        assert final.status == "failed"

    def test_custom_final_answer_included(self):
        plan = _make_plan()
        events = build_timeline(plan, final_answer="LCR ratio is compliant at 150%.")
        final = next(e for e in events if e.stage == "final_answer")
        assert "LCR" in final.detail or "compliant" in final.detail

    def test_no_chain_of_thought_exposed(self):
        plan = _make_plan()
        events = build_timeline(plan)
        all_details = " ".join(e.detail for e in events).lower()
        forbidden = ["chain of thought", "internal reasoning", "scratchpad", "thinking:"]
        for phrase in forbidden:
            assert phrase not in all_details
