"""
Execution monitor for the SAM Planner (Epic 4D).

Tracks execution history of agent plans. Stored in-memory per process
(expandable to a DB-backed store in a future epic without changing the API).
"""

from __future__ import annotations

import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import ClassVar


@dataclass
class StepRecord:
    """Immutable execution record for a single plan step."""

    step_id: str
    tool_name: str
    description: str
    status: str  # completed | failed | skipped
    start_time: str | None
    end_time: str | None
    duration_ms: int | None
    retry_count: int
    error: str | None
    evidence_confidence: str  # HIGH | MEDIUM | LOW | N/A

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "tool_name": self.tool_name,
            "description": self.description,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "retry_count": self.retry_count,
            "error": self.error,
            "evidence_confidence": self.evidence_confidence,
        }


@dataclass
class ExecutionRecord:
    """Full execution record for one agent plan run."""

    execution_id: str
    plan_id: str
    intent: str
    entity_id: str | None
    snapshot_id: str | None
    status: str  # completed | failed | partial
    steps: list[StepRecord] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    completed_at: str | None = None
    total_duration_ms: int | None = None
    steps_completed: int = 0
    steps_failed: int = 0
    steps_skipped: int = 0

    def to_dict(self) -> dict:
        return {
            "execution_id": self.execution_id,
            "plan_id": self.plan_id,
            "intent": self.intent,
            "entity_id": self.entity_id,
            "snapshot_id": self.snapshot_id,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_duration_ms": self.total_duration_ms,
            "steps_completed": self.steps_completed,
            "steps_failed": self.steps_failed,
            "steps_skipped": self.steps_skipped,
        }


class ExecutionMonitor:
    """
    In-memory execution history store.

    Keeps the last MAX_HISTORY execution records. Thread-safe for the
    asyncio single-thread model used by FastAPI.
    """

    MAX_HISTORY: ClassVar[int] = 50

    def __init__(self) -> None:
        self._history: OrderedDict[str, ExecutionRecord] = OrderedDict()

    def record_execution(self, record: ExecutionRecord) -> None:
        """Store an execution record, evicting oldest when at capacity."""
        self._history[record.execution_id] = record
        while len(self._history) > self.MAX_HISTORY:
            self._history.popitem(last=False)

    def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        return self._history.get(execution_id)

    def get_history(self, limit: int = 20) -> list[ExecutionRecord]:
        """Return most-recent-first list of execution records."""
        records = list(self._history.values())
        records.reverse()
        return records[:limit]

    def record_from_plan(self, plan) -> ExecutionRecord:
        """
        Build and store an ExecutionRecord from a completed ExecutionPlan.
        Returns the stored record.
        """
        from .planner.base import StepStatus  # avoid circular at module load

        step_records: list[StepRecord] = []
        for step in plan.steps:
            ev_conf = "N/A"
            if step.evidence and isinstance(step.evidence, dict):
                ev_conf = step.evidence.get("confidence", "N/A")
            step_records.append(StepRecord(
                step_id=step.step_id,
                tool_name=step.tool_name,
                description=step.description,
                status=step.status.value if hasattr(step.status, "value") else str(step.status),
                start_time=step.start_time,
                end_time=step.end_time,
                duration_ms=step.duration_ms,
                retry_count=step.retry_count,
                error=step.error,
                evidence_confidence=ev_conf,
            ))

        completed = sum(1 for s in step_records if s.status == "completed")
        failed = sum(1 for s in step_records if s.status == "failed")
        skipped = sum(1 for s in step_records if s.status == "skipped")

        # Compute total duration
        total_ms: int | None = None
        durations = [s.duration_ms for s in step_records if s.duration_ms is not None]
        if durations:
            total_ms = sum(durations)

        record = ExecutionRecord(
            execution_id=str(uuid.uuid4()),
            plan_id=plan.plan_id,
            intent=plan.intent,
            entity_id=plan.entity_id,
            snapshot_id=plan.snapshot_id,
            status=plan.status.value if hasattr(plan.status, "value") else str(plan.status),
            steps=step_records,
            completed_at=plan.completed_at,
            total_duration_ms=total_ms,
            steps_completed=completed,
            steps_failed=failed,
            steps_skipped=skipped,
        )
        self.record_execution(record)
        return record


# Module-level singleton — shared across all requests in this process
_monitor = ExecutionMonitor()


def get_monitor() -> ExecutionMonitor:
    return _monitor
