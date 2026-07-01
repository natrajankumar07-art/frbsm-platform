"""
Plan executor for the SAM Planner (Epic 4D).

Executes an ExecutionPlan step-by-step, respecting dependencies, handling
retries, and streaming SSE events for the frontend execution timeline.

No financial computation. Calls tools from the ToolRegistry.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from ..tools.base import ToolRegistry
from .base import ExecutionPlan, ExecutionStep, PlanStatus, StepStatus


def _now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


class PlanExecutor:
    """
    Executes an ExecutionPlan by running each step in dependency order.

    Yields SSE-formatted strings: plan_start, step_start, step_complete,
    step_failed, step_skipped, plan_complete, error.
    """

    def __init__(self, registry: ToolRegistry, max_retries: int = 1) -> None:
        self._registry = registry
        self._max_retries = max_retries

    async def execute(
        self, plan: ExecutionPlan, db: AsyncSession
    ):
        """Async generator yielding SSE event strings."""
        plan.status = PlanStatus.EXECUTING

        yield _sse("plan_start", {
            "plan_id": plan.plan_id,
            "intent": plan.intent,
            "total_steps": len(plan.steps),
            "timestamp": _now(),
        })

        # Execute steps in order, respecting dependencies
        for step in plan.steps:
            # Wait for dependencies — skip step if any dep failed
            if not plan.dependencies_met(step):
                failed_deps = [
                    dep_id for dep_id in step.depends_on
                    if (dep := plan.get_step(dep_id)) and dep.status == StepStatus.FAILED
                ]
                if failed_deps:
                    step.mark_skipped(f"Skipped: dependency {failed_deps[0]} failed")
                    yield _sse("step_skipped", {
                        "plan_id": plan.plan_id,
                        "step_id": step.step_id,
                        "tool_name": step.tool_name,
                        "reason": step.error or "dependency not met",
                        "timestamp": _now(),
                    })
                    continue
                # Dependencies still pending — should not happen in linear ordering
                step.mark_skipped("Skipped: dependency not resolved")
                yield _sse("step_skipped", {
                    "plan_id": plan.plan_id,
                    "step_id": step.step_id,
                    "tool_name": step.tool_name,
                    "reason": "dependency not resolved",
                    "timestamp": _now(),
                })
                continue

            # Execute with retry loop
            await self._execute_step_with_retry(plan, step, db)

            if step.status == StepStatus.COMPLETED:
                yield _sse("step_complete", {
                    "plan_id": plan.plan_id,
                    "step_id": step.step_id,
                    "tool_name": step.tool_name,
                    "description": step.description,
                    "duration_ms": step.duration_ms,
                    "evidence": step.evidence,
                    "timestamp": step.end_time or _now(),
                })
            elif step.status == StepStatus.FAILED:
                yield _sse("step_failed", {
                    "plan_id": plan.plan_id,
                    "step_id": step.step_id,
                    "tool_name": step.tool_name,
                    "error": step.error,
                    "retry_count": step.retry_count,
                    "timestamp": step.end_time or _now(),
                })

        # Finalize plan status
        plan.completed_at = _now()
        if plan.has_failures():
            completed = len(plan.completed_steps())
            plan.status = PlanStatus.PARTIAL if completed > 0 else PlanStatus.FAILED
        else:
            plan.status = PlanStatus.COMPLETED

        yield _sse("plan_complete", {
            "plan_id": plan.plan_id,
            "status": plan.status.value,
            "steps_completed": len(plan.completed_steps()),
            "steps_failed": len(plan.failed_steps()),
            "steps_skipped": len(plan.skipped_steps()),
            "completed_at": plan.completed_at,
        })

    async def _execute_step_with_retry(
        self, plan: ExecutionPlan, step: ExecutionStep, db: AsyncSession
    ) -> None:
        """Execute a single step, retrying on failure up to max_retries."""
        tool = self._registry.get(step.tool_name)
        if not tool:
            step.mark_failed(f"Tool '{step.tool_name}' not found in registry")
            return

        for attempt in range(step.max_retries + 1):
            if attempt > 0:
                step.status = StepStatus.RETRYING
                step.retry_count = attempt

            step.mark_running()
            try:
                params = dict(step.params)
                # Inject plan-level entity/snapshot if step params don't override
                if plan.entity_id and "entity_id" not in params:
                    params["entity_id"] = str(plan.entity_id)
                if plan.snapshot_id and "snapshot_id" not in params:
                    params["snapshot_id"] = str(plan.snapshot_id)

                result = await tool.execute(params, db)
                if result.success:
                    step.mark_completed(
                        result=result.data,
                        evidence=result.evidence.to_dict(),
                    )
                    return
                else:
                    if attempt < step.max_retries:
                        continue
                    step.mark_failed(result.error or "Tool returned failure")
            except Exception as exc:
                if attempt < step.max_retries:
                    continue
                step.mark_failed(str(exc))
