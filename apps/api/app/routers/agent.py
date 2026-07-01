"""
Epic 4D — SAM Agent endpoints.

  POST /v1/copilot/agent/chat          — full agentic chat with planning (SSE)
  POST /v1/copilot/agent/plan          — create execution plan (JSON, dry-run)
  GET  /v1/copilot/agent/history       — execution history
  GET  /v1/copilot/agent/alerts        — autonomous monitoring alerts
  GET  /v1/copilot/agent/timeline/{id} — reasoning timeline for a plan
  POST /v1/copilot/agent/analyze-intent — intent analysis (debug/demo)

These endpoints are additive. Epics 4A/4B/4C infrastructure is not modified.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..dependencies import DBSession
from ..schemas.agent import (
    AgentChatRequest,
    AlertResponse,
    AlertsResponse,
    ExecutionHistoryResponse,
    ExecutionRecordResponse,
    IntentAnalysisResponse,
    PlanRequest,
    PlanResponse,
    StepRecordResponse,
    StepResponse,
    TimelineEventResponse,
    TimelineResponse,
)
from ..services.ai.autonomous_monitor import run_monitoring_checks
from ..services.ai.execution_monitor import get_monitor
from ..services.ai.memory import get_session_memory
from ..services.ai.planner import ExecutionPlan, PlanExecutor, analyze_intent, select_tools
from ..services.ai.reasoning_timeline import build_timeline
from ..services.ai.tools import registry

router = APIRouter(prefix="/v1/copilot/agent", tags=["SAM Agent"])
logger = structlog.get_logger(__name__)

_executor = PlanExecutor(registry=registry)
_monitor = get_monitor()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plan_to_response(plan: ExecutionPlan) -> PlanResponse:
    d = plan.to_dict()
    return PlanResponse(
        plan_id=d["plan_id"],
        intent=d["intent"],
        status=d["status"],
        entity_id=d.get("entity_id"),
        snapshot_id=d.get("snapshot_id"),
        entity_name=d.get("entity_name"),
        snapshot_date=d.get("snapshot_date"),
        created_at=d["created_at"],
        completed_at=d.get("completed_at"),
        steps=[StepResponse(**s) for s in d["steps"]],
        steps_total=d["steps_total"],
        steps_completed=d["steps_completed"],
        steps_failed=d["steps_failed"],
        steps_skipped=d["steps_skipped"],
    )


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# ---------------------------------------------------------------------------
# Agentic chat — full planning + execution + timeline (SSE)
# ---------------------------------------------------------------------------

@router.post("/chat")
async def agent_chat(
    body: AgentChatRequest,
    db: DBSession,
) -> StreamingResponse:
    """
    Full SAM agentic chat.

    Runs intent analysis → planning → tool execution → reasoning timeline,
    streaming SSE events for each phase. The frontend renders the execution
    timeline in real time.
    """
    memory = await get_session_memory(db, body.session_id) if body.session_id else None

    async def _stream():
        # --- Phase 1: Intent analysis ---
        mem_preamble = memory.build_context_preamble() if memory else ""
        analysis = analyze_intent(body.user_message, mem_preamble)

        yield _sse("intent_analyzed", {
            "intent": analysis.primary_intent,
            "domains": analysis.domains,
            "confidence": analysis.confidence,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        })

        # Resolve conversational references from memory
        resolved: dict = {}
        if memory:
            for ref_key in ("entity_reference", "snapshot_reference", "time_reference", "repeat_reference"):
                ref_val = getattr(analysis, ref_key, None)
                if ref_val:
                    resolved.update(memory.resolve_reference(ref_val))

        entity_id = str(body.entity_id) if body.entity_id else resolved.get("entity_id")
        snapshot_id = str(body.snapshot_id) if body.snapshot_id else resolved.get("snapshot_id")

        # --- Phase 2: Planning ---
        steps = select_tools(analysis, entity_id=entity_id, snapshot_id=snapshot_id)
        plan = ExecutionPlan.create(
            intent=body.user_message,
            steps=steps,
            entity_id=entity_id,
            snapshot_id=snapshot_id,
        )

        yield _sse("plan_created", {
            "plan_id": plan.plan_id,
            "total_steps": len(plan.steps),
            "tool_names": [s.tool_name for s in plan.steps],
            "timestamp": plan.created_at,
        })

        # --- Phase 3: Execute plan (streams step events) ---
        async for event in _executor.execute(plan, db):
            yield event

        # --- Phase 4: Record execution history ---
        record = _monitor.record_from_plan(plan)

        # --- Phase 5: Reasoning timeline ---
        timeline_events = build_timeline(plan)
        yield _sse("timeline_ready", {
            "plan_id": plan.plan_id,
            "execution_id": record.execution_id,
            "events": [e.to_dict() for e in timeline_events],
        })

        # --- Phase 6: Done ---
        completed = len(plan.completed_steps())
        total = len(plan.steps)
        yield _sse("agent_done", {
            "plan_id": plan.plan_id,
            "execution_id": record.execution_id,
            "status": plan.status.value,
            "steps_completed": completed,
            "steps_total": total,
            "message": (
                f"SAM completed {completed}/{total} steps. "
                f"Review the evidence panel for source data."
            ),
        })

    return StreamingResponse(_stream(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Plan dry-run (JSON, no execution)
# ---------------------------------------------------------------------------

@router.post("/plan", response_model=PlanResponse)
async def create_plan(body: PlanRequest) -> PlanResponse:
    """
    Create an execution plan without running it.
    Useful for preview, debugging, and user confirmation flows.
    """
    analysis = analyze_intent(body.user_message)
    steps = select_tools(
        analysis,
        entity_id=str(body.entity_id) if body.entity_id else None,
        snapshot_id=str(body.snapshot_id) if body.snapshot_id else None,
    )
    plan = ExecutionPlan.create(
        intent=body.user_message,
        steps=steps,
        entity_id=str(body.entity_id) if body.entity_id else None,
        snapshot_id=str(body.snapshot_id) if body.snapshot_id else None,
    )
    logger.info("plan_created", plan_id=plan.plan_id, steps=len(plan.steps))
    return _plan_to_response(plan)


# ---------------------------------------------------------------------------
# Execution history
# ---------------------------------------------------------------------------

@router.get("/history", response_model=ExecutionHistoryResponse)
async def get_execution_history(limit: int = 20) -> ExecutionHistoryResponse:
    """Return most-recent-first execution history."""
    records = _monitor.get_history(limit=min(limit, 50))
    return ExecutionHistoryResponse(
        executions=[
            ExecutionRecordResponse(
                execution_id=r.execution_id,
                plan_id=r.plan_id,
                intent=r.intent,
                entity_id=r.entity_id,
                snapshot_id=r.snapshot_id,
                status=r.status,
                steps=[StepRecordResponse(**s.to_dict()) for s in r.steps],
                started_at=r.started_at,
                completed_at=r.completed_at,
                total_duration_ms=r.total_duration_ms,
                steps_completed=r.steps_completed,
                steps_failed=r.steps_failed,
                steps_skipped=r.steps_skipped,
            )
            for r in records
        ],
        total=len(records),
    )


# ---------------------------------------------------------------------------
# Autonomous monitoring alerts
# ---------------------------------------------------------------------------

@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(db: DBSession) -> AlertsResponse:
    """
    Run all autonomous monitoring checks and return structured alerts.
    Checks LCR, NSFR, and Capital ratios against regulatory thresholds.
    """
    alerts = await run_monitoring_checks(db)
    critical = sum(1 for a in alerts if a.severity == "critical")
    high = sum(1 for a in alerts if a.severity == "high")
    medium = sum(1 for a in alerts if a.severity == "medium")

    return AlertsResponse(
        alerts=[AlertResponse(**a.to_dict()) for a in alerts],
        total=len(alerts),
        critical=critical,
        high=high,
        medium=medium,
    )


# ---------------------------------------------------------------------------
# Reasoning timeline
# ---------------------------------------------------------------------------

@router.get("/timeline/{plan_id}", response_model=TimelineResponse)
async def get_timeline(plan_id: str) -> TimelineResponse:
    """
    Return the reasoning timeline for a past execution.
    Looks up the execution record from in-memory history.
    """
    # Find the record by plan_id
    history = _monitor.get_history(limit=50)
    record = next((r for r in history if r.plan_id == plan_id), None)

    if not record:
        return TimelineResponse(plan_id=plan_id, events=[
            TimelineEventResponse(
                stage="unknown",
                label="Not Found",
                detail=f"No execution record found for plan {plan_id}",
                timestamp=datetime.now(tz=timezone.utc).isoformat(),
                status="failed",
            )
        ])

    # Reconstruct minimal plan for timeline builder
    from ..services.ai.planner.base import ExecutionStep, PlanStatus, StepStatus  # noqa: PLC0415

    pseudo_steps: list[ExecutionStep] = []
    for s in record.steps:
        step = ExecutionStep(
            step_id=s.step_id,
            tool_name=s.tool_name,
            description=s.description,
            status=StepStatus(s.status),
            start_time=s.start_time,
            end_time=s.end_time,
            duration_ms=s.duration_ms,
            retry_count=s.retry_count,
            error=s.error,
            evidence={"confidence": s.evidence_confidence} if s.evidence_confidence != "N/A" else None,
        )
        pseudo_steps.append(step)

    pseudo_plan = ExecutionPlan(
        plan_id=record.plan_id,
        intent=record.intent,
        steps=pseudo_steps,
        status=PlanStatus(record.status),
        entity_id=record.entity_id,
        snapshot_id=record.snapshot_id,
        created_at=record.started_at,
        completed_at=record.completed_at,
    )

    events = build_timeline(pseudo_plan)
    return TimelineResponse(
        plan_id=plan_id,
        events=[TimelineEventResponse(**e.to_dict()) for e in events],
    )


# ---------------------------------------------------------------------------
# Intent analysis (demo/debug)
# ---------------------------------------------------------------------------

@router.post("/analyze-intent", response_model=IntentAnalysisResponse)
async def analyze_intent_endpoint(body: PlanRequest) -> IntentAnalysisResponse:
    """Analyze intent of a message without executing any tools."""
    analysis = analyze_intent(body.user_message)
    return IntentAnalysisResponse(
        primary_intent=analysis.primary_intent,
        domains=analysis.domains,
        required_tools=analysis.required_tools,
        time_reference=analysis.time_reference,
        entity_reference=analysis.entity_reference,
        repeat_reference=analysis.repeat_reference,
        report_type_hint=analysis.report_type_hint,
        confidence=analysis.confidence,
    )
