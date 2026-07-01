"""
Core dataclasses for the SAM Planner (Epic 4D).

ExecutionPlan and ExecutionStep model the agent's decomposed work order.
TimelineEvent models the user-facing explainability timeline.
Nothing here computes financial ratios or calls engine functions.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class PlanStatus(str, Enum):
    DRAFT = "draft"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class TimelineStage(str, Enum):
    INTENT = "intent"
    PLANNING = "planning"
    TOOL_CALLS = "tool_calls"
    EVIDENCE_COLLECTION = "evidence_collection"
    REASONING = "reasoning"
    REPORT_GENERATION = "report_generation"
    FINAL_ANSWER = "final_answer"

    @property
    def label(self) -> str:
        return {
            TimelineStage.INTENT: "Intent Analysis",
            TimelineStage.PLANNING: "Execution Planning",
            TimelineStage.TOOL_CALLS: "Tool Execution",
            TimelineStage.EVIDENCE_COLLECTION: "Evidence Collection",
            TimelineStage.REASONING: "Reasoning",
            TimelineStage.REPORT_GENERATION: "Report Generation",
            TimelineStage.FINAL_ANSWER: "Final Answer",
        }[self]


@dataclass
class TimelineEvent:
    """One step in the user-facing explainability timeline (never chain-of-thought)."""

    stage: str  # TimelineStage value
    label: str
    detail: str
    timestamp: str
    status: str = "completed"  # completed | running | pending | failed

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutionStep:
    """One tool invocation within an ExecutionPlan."""

    step_id: str
    tool_name: str
    description: str
    params: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)  # step_ids that must complete first
    status: StepStatus = StepStatus.PENDING
    result: dict | None = None
    error: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    duration_ms: int | None = None
    retry_count: int = 0
    max_retries: int = 1
    evidence: dict | None = None

    def mark_running(self) -> None:
        self.status = StepStatus.RUNNING
        self.start_time = datetime.now(tz=timezone.utc).isoformat()

    def mark_completed(self, result: dict, evidence: dict | None = None) -> None:
        self.status = StepStatus.COMPLETED
        self.result = result
        self.evidence = evidence
        self.end_time = datetime.now(tz=timezone.utc).isoformat()
        if self.start_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration_ms = int((end - start).total_seconds() * 1000)

    def mark_failed(self, error: str) -> None:
        self.status = StepStatus.FAILED
        self.error = error
        self.end_time = datetime.now(tz=timezone.utc).isoformat()
        if self.start_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration_ms = int((end - start).total_seconds() * 1000)

    def mark_skipped(self, reason: str = "") -> None:
        self.status = StepStatus.SKIPPED
        if reason:
            self.error = reason

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "tool_name": self.tool_name,
            "description": self.description,
            "params": self.params,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "evidence": self.evidence,
        }


@dataclass
class ExecutionPlan:
    """Decomposed execution plan produced by the SAM Planner."""

    plan_id: str
    intent: str
    steps: list[ExecutionStep]
    status: PlanStatus = PlanStatus.DRAFT
    entity_id: str | None = None
    snapshot_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    completed_at: str | None = None
    entity_name: str | None = None
    snapshot_date: str | None = None

    @classmethod
    def create(
        cls,
        intent: str,
        steps: list[ExecutionStep],
        entity_id: str | None = None,
        snapshot_id: str | None = None,
        entity_name: str | None = None,
        snapshot_date: str | None = None,
    ) -> "ExecutionPlan":
        return cls(
            plan_id=str(uuid.uuid4()),
            intent=intent,
            steps=steps,
            entity_id=entity_id,
            snapshot_id=snapshot_id,
            entity_name=entity_name,
            snapshot_date=snapshot_date,
        )

    def pending_steps(self) -> list[ExecutionStep]:
        return [s for s in self.steps if s.status == StepStatus.PENDING]

    def completed_steps(self) -> list[ExecutionStep]:
        return [s for s in self.steps if s.status == StepStatus.COMPLETED]

    def failed_steps(self) -> list[ExecutionStep]:
        return [s for s in self.steps if s.status == StepStatus.FAILED]

    def skipped_steps(self) -> list[ExecutionStep]:
        return [s for s in self.steps if s.status == StepStatus.SKIPPED]

    def is_complete(self) -> bool:
        return all(
            s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED, StepStatus.FAILED)
            for s in self.steps
        )

    def has_failures(self) -> bool:
        return any(s.status == StepStatus.FAILED for s in self.steps)

    def get_step(self, step_id: str) -> ExecutionStep | None:
        return next((s for s in self.steps if s.step_id == step_id), None)

    def dependencies_met(self, step: ExecutionStep) -> bool:
        for dep_id in step.depends_on:
            dep = self.get_step(dep_id)
            if dep is None or dep.status not in (StepStatus.COMPLETED, StepStatus.SKIPPED):
                return False
        return True

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "intent": self.intent,
            "status": self.status.value,
            "entity_id": self.entity_id,
            "snapshot_id": self.snapshot_id,
            "entity_name": self.entity_name,
            "snapshot_date": self.snapshot_date,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "steps": [s.to_dict() for s in self.steps],
            "steps_total": len(self.steps),
            "steps_completed": len(self.completed_steps()),
            "steps_failed": len(self.failed_steps()),
            "steps_skipped": len(self.skipped_steps()),
        }
