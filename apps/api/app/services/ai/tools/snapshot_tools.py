"""Snapshot tools: get_snapshots, compare_snapshots, explain_changes."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.models.balance_sheet import BalanceSheetSummaryModel
from ....db.models.capital import CapitalResultModel
from ....db.models.lcr import LCRResultModel
from ....db.models.legal_entity import LegalEntityModel
from ....db.models.nsfr import NSFRResultModel
from ....db.models.snapshot import SnapshotModel
from .base import BaseTool, ToolEvidence, ToolResult

_SOURCE_TABLES = ["lcr_results", "nsfr_results", "capital_results", "balance_sheet_summaries"]
_REG_REFS = ["BCBS LCR30/40", "BCBS NSF20", "BCBS CAP10", "BCBS LEV10"]


class GetSnapshotsTool(BaseTool):
    name = "get_snapshots"
    description = (
        "List available reporting snapshots with their dates, status (draft/locked/filed), "
        "and position counts. Optionally filter by status."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["draft", "locked", "filed"],
                "description": "Filter snapshots by lifecycle status.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of snapshots to return (default 10).",
                "default": 10,
            },
        },
        "required": [],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        q = (
            select(SnapshotModel)
            .order_by(SnapshotModel.reporting_date.desc())
            .limit(int(params.get("limit", 10)))
        )
        if params.get("status"):
            q = q.where(SnapshotModel.status == params["status"])

        rows = (await db.scalars(q)).all()
        if not rows:
            return self._error_result("No snapshots found.")

        snapshots = [
            {
                "id": str(s.id),
                "reporting_date": str(s.reporting_date),
                "status": s.status,
                "position_count": s.position_count,
                "frozen_by": s.frozen_by,
                "notes": s.notes,
            }
            for s in rows
        ]

        md = [
            f"## Reporting Snapshots ({len(snapshots)} found)",
            "",
            "| Date | Status | Positions | Frozen By |",
            "|---|---|---|---|",
        ]
        for s in snapshots:
            md.append(
                f"| {s['reporting_date']} | {s['status']} "
                f"| {s['position_count']} | {s['frozen_by']} |"
            )

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={"snapshots": snapshots, "total": len(snapshots)},
            evidence=ToolEvidence(source_tables=["snapshots"], confidence="HIGH"),
            markdown="\n".join(md),
        )


class CompareSnapshotsTool(BaseTool):
    name = "compare_snapshots"
    description = (
        "Compare all regulatory metrics between two reporting snapshots for a given entity. "
        "Shows absolute and percentage changes across LCR, NSFR, Capital, and Balance Sheet."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "entity_id": {
                "type": "string",
                "description": "UUID of the legal entity to compare.",
            },
            "snapshot_id_a": {
                "type": "string",
                "description": "UUID of the baseline snapshot (earlier date).",
            },
            "snapshot_id_b": {
                "type": "string",
                "description": "UUID of the comparison snapshot (later date).",
            },
        },
        "required": ["entity_id", "snapshot_id_a", "snapshot_id_b"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        try:
            eid = uuid.UUID(params["entity_id"])
            sid_a = uuid.UUID(params["snapshot_id_a"])
            sid_b = uuid.UUID(params["snapshot_id_b"])
        except (ValueError, KeyError) as exc:
            return self._error_result(f"Invalid parameter: {exc}")

        entity = await db.scalar(select(LegalEntityModel).where(LegalEntityModel.id == eid))
        snap_a = await db.scalar(select(SnapshotModel).where(SnapshotModel.id == sid_a))
        snap_b = await db.scalar(select(SnapshotModel).where(SnapshotModel.id == sid_b))

        if not entity or not snap_a or not snap_b:
            return self._error_result("Entity or one of the snapshots not found.")

        async def _metrics(snap_id: uuid.UUID) -> dict:
            lcr = await db.scalar(
                select(LCRResultModel).where(
                    LCRResultModel.snapshot_id == snap_id,
                    LCRResultModel.entity_id == eid,
                )
            )
            nsfr = await db.scalar(
                select(NSFRResultModel).where(
                    NSFRResultModel.snapshot_id == snap_id,
                    NSFRResultModel.entity_id == eid,
                )
            )
            cap = await db.scalar(
                select(CapitalResultModel).where(
                    CapitalResultModel.snapshot_id == snap_id,
                    CapitalResultModel.entity_id == eid,
                )
            )
            bs = await db.scalar(
                select(BalanceSheetSummaryModel).where(
                    BalanceSheetSummaryModel.snapshot_id == snap_id,
                    BalanceSheetSummaryModel.entity_id == eid,
                )
            )
            return {
                "lcr_ratio": float(lcr.lcr_ratio) if lcr else None,
                "nsfr_ratio": float(nsfr.nsfr_ratio) if nsfr else None,
                "cet1_ratio": float(cap.cet1_ratio) if cap else None,
                "tier1_ratio": float(cap.tier1_ratio) if cap else None,
                "total_capital_ratio": float(cap.total_capital_ratio) if cap else None,
                "leverage_ratio": float(cap.leverage_ratio) if cap else None,
                "total_assets": float(bs.total_assets) if bs else None,
                "total_equity": float(bs.total_equity) if bs else None,
                "hqla_total": float(lcr.hqla_total) if lcr else None,
                "asf": float(nsfr.available_stable_funding) if nsfr else None,
                "rsf": float(nsfr.required_stable_funding) if nsfr else None,
            }

        ma = await _metrics(sid_a)
        mb = await _metrics(sid_b)

        def _delta(key: str, pct: bool = False) -> str:
            va, vb = ma.get(key), mb.get(key)
            if va is None or vb is None:
                return "N/A"
            delta = (vb - va) * (100 if pct else 1)
            sign = "+" if delta >= 0 else ""
            unit = "pp" if pct else ""
            return f"{sign}{delta:.2f}{unit}"

        def _fmt(v: float | None, pct: bool = False) -> str:
            if v is None:
                return "N/A"
            return f"{v * 100:.2f}%" if pct else f"{v:,.0f}"

        md = [
            f"## Snapshot Comparison: {snap_a.reporting_date} → {snap_b.reporting_date}",
            f"**Entity:** {entity.name}",
            "",
            "| Metric | Baseline | Comparison | Change |",
            "|---|---|---|---|",
            f"| LCR Ratio | {_fmt(ma['lcr_ratio'], True)} | {_fmt(mb['lcr_ratio'], True)} | {_delta('lcr_ratio', True)} |",
            f"| NSFR Ratio | {_fmt(ma['nsfr_ratio'], True)} | {_fmt(mb['nsfr_ratio'], True)} | {_delta('nsfr_ratio', True)} |",
            f"| CET1 Ratio | {_fmt(ma['cet1_ratio'], True)} | {_fmt(mb['cet1_ratio'], True)} | {_delta('cet1_ratio', True)} |",
            f"| Total Capital Ratio | {_fmt(ma['total_capital_ratio'], True)} | {_fmt(mb['total_capital_ratio'], True)} | {_delta('total_capital_ratio', True)} |",
            f"| Leverage Ratio | {_fmt(ma['leverage_ratio'], True)} | {_fmt(mb['leverage_ratio'], True)} | {_delta('leverage_ratio', True)} |",
            f"| HQLA Total | {_fmt(ma['hqla_total'])} | {_fmt(mb['hqla_total'])} | {_delta('hqla_total')} |",
            f"| ASF | {_fmt(ma['asf'])} | {_fmt(mb['asf'])} | {_delta('asf')} |",
            f"| Total Assets | {_fmt(ma['total_assets'])} | {_fmt(mb['total_assets'])} | {_delta('total_assets')} |",
        ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={
                "entity": entity.name,
                "baseline": {"snapshot_date": str(snap_a.reporting_date), "metrics": ma},
                "comparison": {"snapshot_date": str(snap_b.reporting_date), "metrics": mb},
            },
            evidence=ToolEvidence(
                entity=entity.name,
                snapshot_date=f"{snap_a.reporting_date} → {snap_b.reporting_date}",
                regulatory_refs=_REG_REFS,
                source_tables=_SOURCE_TABLES,
                confidence="HIGH",
            ),
            markdown="\n".join(md),
        )


class ExplainChangesTool(BaseTool):
    name = "explain_changes"
    description = (
        "Generate a narrative explanation of the changes between two reporting periods "
        "for a given entity. Identifies key drivers, regulatory impacts, and management signals. "
        "All numbers from pre-computed engine results only."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "entity_id": {
                "type": "string",
                "description": "UUID of the legal entity.",
            },
            "snapshot_id_a": {
                "type": "string",
                "description": "UUID of the baseline (earlier) snapshot.",
            },
            "snapshot_id_b": {
                "type": "string",
                "description": "UUID of the comparison (later) snapshot.",
            },
        },
        "required": ["entity_id", "snapshot_id_a", "snapshot_id_b"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        # Delegate to CompareSnapshotsTool then add narrative framing
        compare = CompareSnapshotsTool()
        base_result = await compare.execute(params, db)
        if not base_result.success:
            return base_result

        data = base_result.data
        entity = data["entity"]
        base_date = data["baseline"]["snapshot_date"]
        comp_date = data["comparison"]["snapshot_date"]
        ma = data["baseline"]["metrics"]
        mb = data["comparison"]["metrics"]

        observations: list[str] = []

        for metric_key, label, min_threshold in [
            ("lcr_ratio", "LCR", 1.0),
            ("nsfr_ratio", "NSFR", 1.0),
            ("cet1_ratio", "CET1", 0.045),
            ("total_capital_ratio", "Total Capital Ratio", 0.08),
        ]:
            va, vb = ma.get(metric_key), mb.get(metric_key)
            if va is None or vb is None:
                continue
            delta_pp = (vb - va) * 100
            direction = "increased" if delta_pp > 0 else "decreased"
            headroom = (vb - min_threshold) * 100
            observations.append(
                f"- **{label}** {direction} by {abs(delta_pp):.2f}pp "
                f"({va * 100:.2f}% → {vb * 100:.2f}%). "
                f"Current headroom above minimum: {headroom:.2f}pp."
            )

        if ma.get("total_assets") and mb.get("total_assets"):
            assets_change_pct = (mb["total_assets"] - ma["total_assets"]) / ma["total_assets"] * 100
            observations.append(
                f"- **Balance Sheet** {'expanded' if assets_change_pct > 0 else 'contracted'} "
                f"by {abs(assets_change_pct):.2f}% period-over-period."
            )

        md = [
            f"## Period Change Narrative — {entity}",
            f"**Reporting Period:** {base_date} → {comp_date}",
            "",
            "### Key Observations",
            *observations,
            "",
            "### Regulatory Impact Assessment",
            "All ratios sourced from BSM deterministic engines. "
            "Changes reflect underlying position movements, not modelling adjustments.",
            "",
            base_result.markdown,
        ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data=base_result.data,
            evidence=base_result.evidence,
            markdown="\n".join(md),
        )
