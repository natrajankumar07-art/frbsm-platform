"""
Reasoning timeline for the SAM Planner (Epic 4D).

Builds a user-facing explainability timeline from an ExecutionPlan.
Never exposes chain-of-thought — only high-level stages are surfaced.

Timeline stages: Intent → Planning → Tool Calls → Evidence Collection →
                 Reasoning → Report Generation → Final Answer
"""

from __future__ import annotations

from datetime import datetime, timezone

from .planner.base import ExecutionPlan, PlanStatus, StepStatus, TimelineEvent, TimelineStage


def _now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def build_timeline(plan: ExecutionPlan, final_answer: str = "") -> list[TimelineEvent]:
    """
    Convert an ExecutionPlan into a user-facing timeline.

    High-level only — no chain-of-thought, no internal tool parameters exposed.
    """
    events: list[TimelineEvent] = []

    # 1. Intent
    events.append(TimelineEvent(
        stage=TimelineStage.INTENT.value,
        label=TimelineStage.INTENT.label,
        detail=_truncate(plan.intent, 120),
        timestamp=plan.created_at,
        status="completed",
    ))

    # 2. Planning
    step_count = len(plan.steps)
    domain_hints = _extract_domains(plan)
    events.append(TimelineEvent(
        stage=TimelineStage.PLANNING.value,
        label=TimelineStage.PLANNING.label,
        detail=f"Decomposed into {step_count} step{'s' if step_count != 1 else ''}"
               + (f" across {domain_hints}" if domain_hints else ""),
        timestamp=plan.created_at,
        status="completed",
    ))

    # 3. Tool calls — one event per completed/failed step (descriptions only)
    tool_call_steps = [
        s for s in plan.steps
        if s.status in (StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED)
    ]
    if tool_call_steps:
        tool_names = list(dict.fromkeys(s.tool_name for s in tool_call_steps))
        failed_tools = [s.tool_name for s in tool_call_steps if s.status == StepStatus.FAILED]
        detail = f"Executed: {', '.join(tool_names[:4])}"
        if len(tool_names) > 4:
            detail += f" +{len(tool_names) - 4} more"
        if failed_tools:
            detail += f" | {len(failed_tools)} failed"
        tc_status = "failed" if len(failed_tools) == len(tool_call_steps) else "completed"
        events.append(TimelineEvent(
            stage=TimelineStage.TOOL_CALLS.value,
            label=TimelineStage.TOOL_CALLS.label,
            detail=detail,
            timestamp=_first_run_time(plan) or plan.created_at,
            status=tc_status,
        ))

    # 4. Evidence collection
    evidence_steps = [s for s in plan.steps if s.evidence and s.status == StepStatus.COMPLETED]
    if evidence_steps:
        confidences = [s.evidence.get("confidence", "N/A") for s in evidence_steps if s.evidence]
        high = sum(1 for c in confidences if c == "HIGH")
        detail = f"Collected evidence from {len(evidence_steps)} source{'s' if len(evidence_steps) != 1 else ''}"
        if high:
            detail += f" — {high} HIGH confidence"
        events.append(TimelineEvent(
            stage=TimelineStage.EVIDENCE_COLLECTION.value,
            label=TimelineStage.EVIDENCE_COLLECTION.label,
            detail=detail,
            timestamp=_last_end_time(plan) or plan.created_at,
            status="completed",
        ))

    # 5. Reasoning (only if plan ran successfully)
    if plan.status in (PlanStatus.COMPLETED, PlanStatus.PARTIAL):
        events.append(TimelineEvent(
            stage=TimelineStage.REASONING.value,
            label=TimelineStage.REASONING.label,
            detail="Applied banking intelligence to synthesize findings",
            timestamp=plan.completed_at or _now(),
            status="completed",
        ))

    # 6. Report generation (only if a report tool ran)
    report_tools = {"generate_executive_summary", "generate_board_commentary",
                    "generate_cro_commentary", "generate_ceo_commentary",
                    "generate_icaap_summary", "generate_ilaap_summary",
                    "generate_basel3_compliance"}
    report_steps = [s for s in plan.steps if s.tool_name in report_tools and s.status == StepStatus.COMPLETED]
    if report_steps:
        events.append(TimelineEvent(
            stage=TimelineStage.REPORT_GENERATION.value,
            label=TimelineStage.REPORT_GENERATION.label,
            detail=f"Generated report using {report_steps[0].tool_name.replace('_', ' ')}",
            timestamp=report_steps[0].end_time or _now(),
            status="completed",
        ))

    # 7. Final answer
    if plan.status in (PlanStatus.COMPLETED, PlanStatus.PARTIAL):
        completed = len([s for s in plan.steps if s.status == StepStatus.COMPLETED])
        total = len(plan.steps)
        detail = f"Analysis complete — {completed}/{total} steps succeeded"
        if final_answer:
            detail = _truncate(final_answer, 120)
        events.append(TimelineEvent(
            stage=TimelineStage.FINAL_ANSWER.value,
            label=TimelineStage.FINAL_ANSWER.label,
            detail=detail,
            timestamp=plan.completed_at or _now(),
            status="completed",
        ))
    elif plan.status == PlanStatus.FAILED:
        events.append(TimelineEvent(
            stage=TimelineStage.FINAL_ANSWER.value,
            label=TimelineStage.FINAL_ANSWER.label,
            detail="Execution failed — check individual step errors",
            timestamp=plan.completed_at or _now(),
            status="failed",
        ))

    return events


def _truncate(text: str, max_len: int) -> str:
    return text if len(text) <= max_len else text[:max_len - 3] + "..."


def _extract_domains(plan: ExecutionPlan) -> str:
    domain_map = {
        "lcr": "LCR", "nsfr": "NSFR", "capital": "Capital",
        "balance_sheet": "Balance Sheet", "stress": "Stress Testing",
        "regulatory": "Regulatory", "alm": "ALM",
    }
    found: list[str] = []
    intent_lower = plan.intent.lower()
    for key, label in domain_map.items():
        if key in intent_lower:
            found.append(label)
    return ", ".join(found[:3]) if found else ""


def _first_run_time(plan: ExecutionPlan) -> str | None:
    for step in plan.steps:
        if step.start_time:
            return step.start_time
    return None


def _last_end_time(plan: ExecutionPlan) -> str | None:
    last: str | None = None
    for step in plan.steps:
        if step.end_time:
            last = step.end_time
    return last
