"""Entity tools: list_entities, compare_entities."""

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


class ListEntitiesTool(BaseTool):
    name = "list_entities"
    description = (
        "List all legal entities registered on the BSM platform. "
        "Returns entity codes, names, jurisdictions, regulator, and whether "
        "each entity is the primary reporting entity."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "jurisdiction": {
                "type": "string",
                "description": "Optional ISO country code to filter by jurisdiction (e.g. 'IN').",
            },
            "reporting_only": {
                "type": "boolean",
                "description": "If true, return only is_reporting_entity=true entities.",
            },
        },
        "required": [],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        q = select(LegalEntityModel).order_by(
            LegalEntityModel.is_reporting_entity.desc(),
            LegalEntityModel.name,
        )
        if params.get("jurisdiction"):
            q = q.where(LegalEntityModel.jurisdiction == params["jurisdiction"])
        if params.get("reporting_only"):
            q = q.where(LegalEntityModel.is_reporting_entity.is_(True))

        rows = (await db.scalars(q)).all()
        if not rows:
            return self._error_result("No entities found matching the filter criteria.")

        entities = [
            {
                "id": str(e.id),
                "code": e.code,
                "name": e.name,
                "entity_type": e.entity_type,
                "jurisdiction": e.jurisdiction,
                "regulator": e.regulator,
                "functional_currency": e.functional_currency,
                "is_reporting_entity": e.is_reporting_entity,
                "is_consolidated": e.is_consolidated,
            }
            for e in rows
        ]

        md_lines = [
            f"## Legal Entities ({len(entities)} found)",
            "",
            "| Code | Name | Type | Jurisdiction | Regulator | Reporting? |",
            "|---|---|---|---|---|---|",
        ]
        for e in entities:
            flag = "✓ Primary" if e["is_reporting_entity"] else ""
            md_lines.append(
                f"| {e['code']} | {e['name']} | {e['entity_type']} "
                f"| {e['jurisdiction']} | {e['regulator']} | {flag} |"
            )

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={"entities": entities, "total": len(entities)},
            evidence=ToolEvidence(
                source_tables=["legal_entities"],
                confidence="HIGH",
            ),
            markdown="\n".join(md_lines),
        )


class CompareEntitiesTool(BaseTool):
    name = "compare_entities"
    description = (
        "Compare regulatory metrics (LCR, NSFR, Capital, Balance Sheet) "
        "between two legal entities for the most recent available snapshot. "
        "Useful for group-level or subsidiary comparisons."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "entity_id_a": {
                "type": "string",
                "description": "UUID of the first legal entity.",
            },
            "entity_id_b": {
                "type": "string",
                "description": "UUID of the second legal entity.",
            },
            "snapshot_id": {
                "type": "string",
                "description": "Optional snapshot UUID. If omitted, the most recent locked snapshot is used.",
            },
        },
        "required": ["entity_id_a", "entity_id_b"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        try:
            eid_a = uuid.UUID(params["entity_id_a"])
            eid_b = uuid.UUID(params["entity_id_b"])
        except (ValueError, KeyError) as exc:
            return self._error_result(f"Invalid entity ID: {exc}")

        # Resolve snapshot
        if params.get("snapshot_id"):
            try:
                snap_id = uuid.UUID(params["snapshot_id"])
            except ValueError as exc:
                return self._error_result(f"Invalid snapshot ID: {exc}")
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

        entity_a = await db.scalar(select(LegalEntityModel).where(LegalEntityModel.id == eid_a))
        entity_b = await db.scalar(select(LegalEntityModel).where(LegalEntityModel.id == eid_b))
        snapshot = await db.scalar(select(SnapshotModel).where(SnapshotModel.id == snap_id))

        if not entity_a or not entity_b or not snapshot:
            return self._error_result("One or more entities or snapshot not found.")

        async def _load_metrics(eid: uuid.UUID) -> dict:
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
                "lcr_ratio": f"{float(lcr.lcr_ratio) * 100:.2f}%" if lcr else "N/A",
                "lcr_pass": lcr.passes if lcr else None,
                "nsfr_ratio": f"{float(nsfr.nsfr_ratio) * 100:.2f}%" if nsfr else "N/A",
                "nsfr_pass": nsfr.passes if nsfr else None,
                "cet1_ratio": f"{float(cap.cet1_ratio) * 100:.2f}%" if cap else "N/A",
                "total_capital_ratio": f"{float(cap.total_capital_ratio) * 100:.2f}%" if cap else "N/A",
                "leverage_ratio": f"{float(cap.leverage_ratio) * 100:.2f}%" if cap else "N/A",
                "total_assets": f"{float(bs.total_assets):,.0f} {bs.currency}" if bs else "N/A",
                "total_equity": f"{float(bs.total_equity):,.0f} {bs.currency}" if bs else "N/A",
            }

        metrics_a = await _load_metrics(eid_a)
        metrics_b = await _load_metrics(eid_b)

        md = [
            f"## Entity Comparison — Snapshot {snapshot.reporting_date}",
            "",
            f"| Metric | {entity_a.name} | {entity_b.name} |",
            "|---|---|---|",
            f"| LCR Ratio | {metrics_a['lcr_ratio']} | {metrics_b['lcr_ratio']} |",
            f"| NSFR Ratio | {metrics_a['nsfr_ratio']} | {metrics_b['nsfr_ratio']} |",
            f"| CET1 Ratio | {metrics_a['cet1_ratio']} | {metrics_b['cet1_ratio']} |",
            f"| Total Capital Ratio | {metrics_a['total_capital_ratio']} | {metrics_b['total_capital_ratio']} |",
            f"| Leverage Ratio | {metrics_a['leverage_ratio']} | {metrics_b['leverage_ratio']} |",
            f"| Total Assets | {metrics_a['total_assets']} | {metrics_b['total_assets']} |",
            f"| Total Equity | {metrics_a['total_equity']} | {metrics_b['total_equity']} |",
        ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={
                "snapshot_date": str(snapshot.reporting_date),
                "entity_a": {"id": str(eid_a), "name": entity_a.name, "metrics": metrics_a},
                "entity_b": {"id": str(eid_b), "name": entity_b.name, "metrics": metrics_b},
            },
            evidence=ToolEvidence(
                snapshot_date=str(snapshot.reporting_date),
                source_tables=["lcr_results", "nsfr_results", "capital_results", "balance_sheet_summaries"],
                confidence="HIGH",
            ),
            markdown="\n".join(md),
        )
