"""
Automatic tool selection for the SAM Planner (Epic 4D).

Given an IntentAnalysis, produces an ordered list of ExecutionStep objects
with resolved parameters. Steps respect dependency ordering so the executor
can run them in the right sequence.

No financial computation. Reads from ToolRegistry but never calls engine functions.
"""

from __future__ import annotations

import uuid

from .base import ExecutionStep
from .intent_analyzer import IntentAnalysis, PrimaryIntent


def _step_id() -> str:
    return str(uuid.uuid4())[:8]


def select_tools(
    analysis: IntentAnalysis,
    entity_id: str | None = None,
    snapshot_id: str | None = None,
) -> list[ExecutionStep]:
    """
    Convert an IntentAnalysis into an ordered list of ExecutionSteps.

    Dependency ordering:
    - list_entities / get_snapshots run first (no deps)
    - compare / analyze / report steps depend on entity+snapshot lookups
    - Executive/report summary steps depend on data retrieval steps
    """
    steps: list[ExecutionStep] = []
    entity_step_id: str | None = None
    snapshot_step_id: str | None = None

    # ------------------------------------------------------------------
    # Step 1 — Entity lookup (always first unless entity already known)
    # ------------------------------------------------------------------
    if not entity_id:
        sid = _step_id()
        steps.append(ExecutionStep(
            step_id=sid,
            tool_name="list_entities",
            description="Discover available banking entities",
            params={},
            depends_on=[],
        ))
        entity_step_id = sid
    else:
        # Entity known — still resolve name via list for context
        sid = _step_id()
        steps.append(ExecutionStep(
            step_id=sid,
            tool_name="list_entities",
            description="Confirm entity context",
            params={},
            depends_on=[],
        ))
        entity_step_id = sid

    # ------------------------------------------------------------------
    # Step 2 — Snapshot lookup
    # ------------------------------------------------------------------
    if not snapshot_id:
        sid = _step_id()
        params: dict = {}
        if entity_id:
            params["entity_id"] = str(entity_id)
        steps.append(ExecutionStep(
            step_id=sid,
            tool_name="get_snapshots",
            description="Retrieve available data snapshots",
            params=params,
            depends_on=[entity_step_id] if entity_step_id else [],
        ))
        snapshot_step_id = sid
    else:
        sid = _step_id()
        steps.append(ExecutionStep(
            step_id=sid,
            tool_name="get_snapshots",
            description="Confirm snapshot context",
            params={"entity_id": str(entity_id)} if entity_id else {},
            depends_on=[entity_step_id] if entity_step_id else [],
        ))
        snapshot_step_id = sid

    lookup_deps = [d for d in [entity_step_id, snapshot_step_id] if d]

    # ------------------------------------------------------------------
    # Step 3 — Intent-specific steps
    # ------------------------------------------------------------------
    intent = analysis.primary_intent

    if intent == PrimaryIntent.COMPARE:
        # Compare snapshots step
        params = {}
        if entity_id:
            params["entity_id"] = str(entity_id)
        if snapshot_id:
            params["snapshot_id_a"] = str(snapshot_id)
        sid = _step_id()
        steps.append(ExecutionStep(
            step_id=sid,
            tool_name="compare_snapshots",
            description="Compare period-over-period metrics",
            params=params,
            depends_on=lookup_deps,
        ))
        if "entit" in analysis.primary_intent or "compare_entities" in analysis.required_tools:
            sid2 = _step_id()
            steps.append(ExecutionStep(
                step_id=sid2,
                tool_name="compare_entities",
                description="Compare entities side-by-side",
                params={"entity_id_a": str(entity_id)} if entity_id else {},
                depends_on=lookup_deps,
            ))

    elif intent == PrimaryIntent.STRESS:
        sid = _step_id()
        steps.append(ExecutionStep(
            step_id=sid,
            tool_name="run_stress_scenario",
            description="Retrieve pre-computed stress scenario results",
            params={"entity_id": str(entity_id)} if entity_id else {},
            depends_on=lookup_deps,
        ))

    elif intent == PrimaryIntent.GENERATE_REPORT:
        report_type = analysis.report_type_hint or "executive_dashboard"
        sid = _step_id()
        steps.append(ExecutionStep(
            step_id=sid,
            tool_name="generate_executive_summary",
            description=f"Generate {report_type.replace('_', ' ').title()} report",
            params={
                "entity_id": str(entity_id) if entity_id else "",
                "snapshot_id": str(snapshot_id) if snapshot_id else "",
                "report_type": report_type,
            },
            depends_on=lookup_deps,
        ))

    elif intent in (PrimaryIntent.ANALYZE, PrimaryIntent.SUMMARIZE, PrimaryIntent.EXPLAIN):
        domains = analysis.domains[:2] if analysis.domains else ["regulatory"]
        domain_to_tool = {
            "lcr": ("summarize_regulatory_results", "Retrieve LCR regulatory summary"),
            "nsfr": ("summarize_regulatory_results", "Retrieve NSFR regulatory summary"),
            "capital": ("summarize_regulatory_results", "Retrieve Capital regulatory summary"),
            "balance_sheet": ("summarize_regulatory_results", "Retrieve Balance Sheet summary"),
            "alm": ("summarize_regulatory_results", "Retrieve ALM summary"),
            "stress": ("run_stress_scenario", "Retrieve stress test results"),
            "regulatory": ("summarize_regulatory_results", "Retrieve regulatory compliance summary"),
            "executive": ("generate_executive_summary", "Retrieve executive overview"),
        }
        seen_tools: set[str] = set()
        for domain in domains:
            tool_name, desc = domain_to_tool.get(domain, ("summarize_regulatory_results", "Retrieve regulatory data"))
            if tool_name not in seen_tools:
                seen_tools.add(tool_name)
                params = {}
                if entity_id:
                    params["entity_id"] = str(entity_id)
                if snapshot_id:
                    params["snapshot_id"] = str(snapshot_id)
                sid = _step_id()
                steps.append(ExecutionStep(
                    step_id=sid,
                    tool_name=tool_name,
                    description=desc,
                    params=params,
                    depends_on=lookup_deps,
                ))

    elif intent == PrimaryIntent.MONITOR:
        sid = _step_id()
        steps.append(ExecutionStep(
            step_id=sid,
            tool_name="summarize_regulatory_results",
            description="Retrieve current regulatory metrics for threshold check",
            params={
                "entity_id": str(entity_id) if entity_id else "",
                "snapshot_id": str(snapshot_id) if snapshot_id else "",
            },
            depends_on=lookup_deps,
        ))

    # ------------------------------------------------------------------
    # If no intent-specific steps added, add a default data retrieval
    # ------------------------------------------------------------------
    if len(steps) <= 2:
        params = {}
        if entity_id:
            params["entity_id"] = str(entity_id)
        if snapshot_id:
            params["snapshot_id"] = str(snapshot_id)
        sid = _step_id()
        steps.append(ExecutionStep(
            step_id=sid,
            tool_name="summarize_regulatory_results",
            description="Retrieve regulatory overview",
            params=params,
            depends_on=lookup_deps,
        ))

    return steps
