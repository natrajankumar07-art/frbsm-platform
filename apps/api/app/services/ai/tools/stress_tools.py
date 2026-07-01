"""Stress test tools: run_stress_scenario, compare_stress_scenarios."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.models.scenario import ScenarioModel
from ....db.models.snapshot import SnapshotModel
from ....db.models.stress_test import StressTestResultModel, StressTestRunModel
from .base import BaseTool, ToolEvidence, ToolResult


class RunStressScenarioTool(BaseTool):
    name = "run_stress_scenario"
    description = (
        "Retrieve the results of an existing stress test run for a given scenario and snapshot. "
        "Shows stressed metric values, absolute and percentage changes from baseline, "
        "and whether any regulatory thresholds are breached. "
        "Note: this reads pre-computed stress results from the database; "
        "it does not re-execute the stress engine."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "scenario_id": {
                "type": "string",
                "description": "UUID of the stress scenario to retrieve results for.",
            },
            "snapshot_id": {
                "type": "string",
                "description": "UUID of the reporting snapshot. If omitted, the most recent locked snapshot is used.",
            },
        },
        "required": ["scenario_id"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        try:
            scenario_id = uuid.UUID(params["scenario_id"])
        except (ValueError, KeyError) as exc:
            return self._error_result(f"Invalid scenario_id: {exc}")

        scenario = await db.scalar(
            select(ScenarioModel).where(ScenarioModel.id == scenario_id)
        )
        if not scenario:
            return self._error_result(f"Scenario {scenario_id} not found.")

        # Resolve snapshot
        if params.get("snapshot_id"):
            try:
                snap_id = uuid.UUID(params["snapshot_id"])
            except ValueError as exc:
                return self._error_result(f"Invalid snapshot_id: {exc}")
        else:
            snap = await db.scalar(
                select(SnapshotModel)
                .where(SnapshotModel.status == "locked")
                .order_by(SnapshotModel.reporting_date.desc())
                .limit(1)
            )
            if not snap:
                return self._error_result("No locked snapshot found.")
            snap_id = snap.id

        snapshot = await db.scalar(
            select(SnapshotModel).where(SnapshotModel.id == snap_id)
        )

        # Find the most recent completed stress run for this scenario + snapshot
        stress_run = await db.scalar(
            select(StressTestRunModel)
            .where(
                StressTestRunModel.scenario_id == scenario_id,
                StressTestRunModel.snapshot_id == snap_id,
                StressTestRunModel.status == "completed",
            )
            .order_by(StressTestRunModel.completed_at.desc())
            .limit(1)
        )

        if not stress_run:
            return ToolResult(
                success=True,
                tool_name=self.name,
                data={
                    "scenario": {"id": str(scenario.id), "name": scenario.name, "type": scenario.scenario_type},
                    "snapshot_date": str(snapshot.reporting_date) if snapshot else "N/A",
                    "results": [],
                },
                evidence=ToolEvidence(
                    snapshot_date=str(snapshot.reporting_date) if snapshot else "",
                    source_tables=["stress_test_runs", "stress_test_results"],
                    confidence="HIGH",
                ),
                markdown=(
                    f"## Stress Scenario: {scenario.name}\n\n"
                    "No completed stress test run found for this scenario and snapshot combination. "
                    "The stress engine has not been executed for these parameters."
                ),
            )

        # Load metric results
        results = (
            await db.scalars(
                select(StressTestResultModel)
                .where(StressTestResultModel.stress_run_id == stress_run.id)
                .order_by(StressTestResultModel.metric_name)
            )
        ).all()

        result_rows = [
            {
                "metric": r.metric_name,
                "baseline": float(r.baseline_value),
                "stressed": float(r.stressed_value),
                "absolute_change": float(r.absolute_change),
                "percentage_change": float(r.percentage_change),
                "threshold": float(r.threshold_value) if r.threshold_value else None,
                "breaches_threshold": r.breaches_threshold,
            }
            for r in results
        ]

        breaches = [r for r in result_rows if r["breaches_threshold"]]

        md = [
            f"## Stress Test Results: {scenario.name}",
            f"**Scenario Type:** {scenario.scenario_type} | "
            f"**Severity:** {scenario.severity or 'N/A'} | "
            f"**Snapshot:** {snapshot.reporting_date if snapshot else 'N/A'}",
            f"**Regulatory Reference:** {scenario.regulatory_reference or 'Internal'}",
            "",
        ]

        if result_rows:
            md += [
                "| Metric | Baseline | Stressed | Change | Threshold | Breach? |",
                "|---|---|---|---|---|---|",
            ]
            for r in result_rows:
                pct = f"{r['percentage_change']:.2f}%"
                thresh = f"{r['threshold']:.4f}" if r["threshold"] else "—"
                breach = "🔴 YES" if r["breaches_threshold"] else "✅ No"
                md.append(
                    f"| {r['metric']} | {r['baseline']:.4f} | {r['stressed']:.4f} "
                    f"| {pct} | {thresh} | {breach} |"
                )
        else:
            md.append("No metric results recorded for this stress run.")

        if breaches:
            md += [
                "",
                f"### ⚠️ Threshold Breaches ({len(breaches)})",
                *[f"- **{b['metric']}**: stressed value {b['stressed']:.4f} breaches threshold {b['threshold']}" for b in breaches],
            ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={
                "scenario": {
                    "id": str(scenario.id),
                    "name": scenario.name,
                    "type": scenario.scenario_type,
                    "severity": scenario.severity,
                    "regulatory_reference": scenario.regulatory_reference,
                },
                "snapshot_date": str(snapshot.reporting_date) if snapshot else "",
                "stress_run_id": str(stress_run.id),
                "results": result_rows,
                "breach_count": len(breaches),
            },
            evidence=ToolEvidence(
                snapshot_date=str(snapshot.reporting_date) if snapshot else "",
                source_tables=["stress_test_runs", "stress_test_results", "scenarios"],
                confidence="HIGH",
            ),
            markdown="\n".join(md),
        )


class CompareStressScenariosTool(BaseTool):
    name = "compare_stress_scenarios"
    description = (
        "Compare the results of two stress scenarios for the same snapshot. "
        "Useful for benchmarking scenario severity or identifying which scenario "
        "poses the greater risk to regulatory compliance."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "scenario_id_a": {
                "type": "string",
                "description": "UUID of the first stress scenario.",
            },
            "scenario_id_b": {
                "type": "string",
                "description": "UUID of the second stress scenario.",
            },
            "snapshot_id": {
                "type": "string",
                "description": "UUID of the snapshot. If omitted, the most recent locked snapshot is used.",
            },
        },
        "required": ["scenario_id_a", "scenario_id_b"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        tool = RunStressScenarioTool()

        params_a = {"scenario_id": params.get("scenario_id_a", ""), "snapshot_id": params.get("snapshot_id")}
        params_b = {"scenario_id": params.get("scenario_id_b", ""), "snapshot_id": params.get("snapshot_id")}

        result_a = await tool.execute({k: v for k, v in params_a.items() if v}, db)
        result_b = await tool.execute({k: v for k, v in params_b.items() if v}, db)

        if not result_a.success:
            return result_a
        if not result_b.success:
            return result_b

        name_a = result_a.data["scenario"]["name"]
        name_b = result_b.data["scenario"]["name"]
        snap_date = result_a.data.get("snapshot_date", "")

        # Build metric comparison
        metrics_a = {r["metric"]: r for r in result_a.data.get("results", [])}
        metrics_b = {r["metric"]: r for r in result_b.data.get("results", [])}
        all_metrics = sorted(set(list(metrics_a.keys()) + list(metrics_b.keys())))

        md = [
            f"## Stress Scenario Comparison — Snapshot {snap_date}",
            "",
            f"| Metric | {name_a} Impact | {name_b} Impact | More Severe |",
            "|---|---|---|---|",
        ]

        for metric in all_metrics:
            ra = metrics_a.get(metric, {})
            rb = metrics_b.get(metric, {})
            ia = ra.get("percentage_change", 0)
            ib = rb.get("percentage_change", 0)
            worse = name_a if abs(ia) > abs(ib) else name_b
            md.append(
                f"| {metric} | {ia:.2f}% | {ib:.2f}% | {worse} |"
            )

        md += [
            "",
            f"**Threshold Breaches — {name_a}:** {result_a.data.get('breach_count', 0)}",
            f"**Threshold Breaches — {name_b}:** {result_b.data.get('breach_count', 0)}",
        ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={
                "scenario_a": result_a.data["scenario"],
                "scenario_b": result_b.data["scenario"],
                "snapshot_date": snap_date,
            },
            evidence=ToolEvidence(
                snapshot_date=snap_date,
                source_tables=["stress_test_runs", "stress_test_results", "scenarios"],
                confidence="HIGH",
            ),
            markdown="\n".join(md),
        )
