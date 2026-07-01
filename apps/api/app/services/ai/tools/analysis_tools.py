"""
Analysis and report generation tools (tools 8–15).

All tools read pre-computed engine results from the DB.
None compute financial ratios.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.models.balance_sheet import BalanceSheetSummaryModel
from ....db.models.capital import CapitalResultModel
from ....db.models.lcr import LCRResultModel
from ....db.models.legal_entity import LegalEntityModel
from ....db.models.nsfr import NSFRResultModel
from ....db.models.snapshot import SnapshotModel
from .base import BaseTool, ToolEvidence, ToolResult

_REG_REFS = [
    "BCBS LCR30/40 (Jan 2013)",
    "BCBS NSF20/30/40 (Oct 2014)",
    "BCBS CAP10 (Jun 2011)",
    "BCBS LEV10 (Jan 2014)",
    "RBI Master Circular Basel III (Jul 2015)",
    "RBI NSFR Guidelines (May 2018)",
]
_SOURCE_TABLES = ["lcr_results", "nsfr_results", "capital_results", "balance_sheet_summaries"]

_ENTITY_SCHEMA = {
    "entity_id": {
        "type": "string",
        "description": "UUID of the legal entity.",
    },
    "snapshot_id": {
        "type": "string",
        "description": "UUID of the snapshot. Defaults to the most recent locked snapshot.",
    },
}


async def _load_all(
    db: AsyncSession, entity_id: uuid.UUID, snapshot_id: uuid.UUID
) -> tuple:
    """Return (entity, snapshot, lcr, nsfr, cap, bs) — any may be None."""
    entity = await db.scalar(
        select(LegalEntityModel).where(LegalEntityModel.id == entity_id)
    )
    snapshot = await db.scalar(
        select(SnapshotModel).where(SnapshotModel.id == snapshot_id)
    )
    lcr = await db.scalar(
        select(LCRResultModel).where(
            LCRResultModel.snapshot_id == snapshot_id,
            LCRResultModel.entity_id == entity_id,
        )
    )
    nsfr = await db.scalar(
        select(NSFRResultModel).where(
            NSFRResultModel.snapshot_id == snapshot_id,
            NSFRResultModel.entity_id == entity_id,
        )
    )
    cap = await db.scalar(
        select(CapitalResultModel).where(
            CapitalResultModel.snapshot_id == snapshot_id,
            CapitalResultModel.entity_id == entity_id,
        )
    )
    bs = await db.scalar(
        select(BalanceSheetSummaryModel).where(
            BalanceSheetSummaryModel.snapshot_id == snapshot_id,
            BalanceSheetSummaryModel.entity_id == entity_id,
        )
    )
    return entity, snapshot, lcr, nsfr, cap, bs


async def _resolve_ids(
    params: dict, db: AsyncSession
) -> tuple[uuid.UUID | None, uuid.UUID | None, str | None]:
    """Parse and resolve entity_id + snapshot_id from params. Returns (eid, sid, error)."""
    try:
        eid = uuid.UUID(params["entity_id"])
    except (ValueError, KeyError) as exc:
        return None, None, f"Invalid entity_id: {exc}"

    if params.get("snapshot_id"):
        try:
            sid = uuid.UUID(params["snapshot_id"])
        except ValueError as exc:
            return eid, None, f"Invalid snapshot_id: {exc}"
    else:
        snap = await db.scalar(
            select(SnapshotModel)
            .where(SnapshotModel.status == "locked")
            .order_by(SnapshotModel.reporting_date.desc())
            .limit(1)
        )
        if not snap:
            return eid, None, "No locked snapshot found."
        sid = snap.id

    return eid, sid, None


def _pct(v) -> str:
    if v is None:
        return "N/A"
    return f"{float(v) * 100:.2f}%"


def _num(v, cur: str = "INR") -> str:
    if v is None:
        return "N/A"
    return f"{float(v):,.2f} {cur}"


def _rag(v: float | None, thresholds: tuple[float, float]) -> str:
    """Return GREEN/AMBER/RED based on value vs thresholds (low, high)."""
    if v is None:
        return "N/A"
    if v >= thresholds[1]:
        return "🟢 GREEN"
    if v >= thresholds[0]:
        return "🟡 AMBER"
    return "🔴 RED"


class SummarizeRegulatoryResultsTool(BaseTool):
    name = "summarize_regulatory_results"
    description = (
        "Summarise all regulatory metrics (LCR, NSFR, Capital, Leverage) "
        "for a given entity and snapshot. Returns a compliance table with "
        "RAG status, headroom above minimums, and regulatory references."
    )
    input_schema = {
        "type": "object",
        "properties": _ENTITY_SCHEMA,
        "required": ["entity_id"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        eid, sid, err = await _resolve_ids(params, db)
        if err:
            return self._error_result(err)

        entity, snapshot, lcr, nsfr, cap, bs = await _load_all(db, eid, sid)
        if not entity or not snapshot:
            return self._error_result("Entity or snapshot not found.")

        rows = []
        if lcr:
            lcr_v = float(lcr.lcr_ratio)
            rows.append(("LCR", _pct(lcr.lcr_ratio), "100.00%", _rag(lcr_v, (1.0, 1.3)), "BCBS LCR30.40"))
        if nsfr:
            nsfr_v = float(nsfr.nsfr_ratio)
            rows.append(("NSFR", _pct(nsfr.nsfr_ratio), "100.00%", _rag(nsfr_v, (1.0, 1.2)), "BCBS NSF20"))
        if cap:
            rows += [
                ("CET1 Ratio", _pct(cap.cet1_ratio), "8.00% (incl. CCB)", _rag(float(cap.cet1_ratio), (0.08, 0.10)), "BCBS CAP10"),
                ("Tier 1 Ratio", _pct(cap.tier1_ratio), "6.00%", _rag(float(cap.tier1_ratio), (0.06, 0.09)), "BCBS CAP10"),
                ("Total Capital Ratio", _pct(cap.total_capital_ratio), "10.875% (RBI)", _rag(float(cap.total_capital_ratio), (0.10875, 0.13)), "RBI Circular"),
                ("Leverage Ratio", _pct(cap.leverage_ratio), "3.50%", _rag(float(cap.leverage_ratio), (0.035, 0.06)), "BCBS LEV10"),
            ]

        md = [
            f"## Regulatory Compliance Summary — {entity.name}",
            f"**Snapshot:** {snapshot.reporting_date} | **Status:** {snapshot.status.upper()}",
            "",
            "| Metric | Actual | Minimum | Status | Reference |",
            "|---|---|---|---|---|",
        ]
        for row in rows:
            md.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |")

        if bs:
            md += [
                "",
                "### Balance Sheet Summary",
                f"| Total Assets | {_num(bs.total_assets, bs.currency)} |",
                f"| Total Liabilities | {_num(bs.total_liabilities, bs.currency)} |",
                f"| Total Equity | {_num(bs.total_equity, bs.currency)} |",
                f"| Off-Balance Sheet | {_num(bs.total_off_balance_sheet, bs.currency)} |",
            ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={
                "entity": entity.name,
                "snapshot_date": str(snapshot.reporting_date),
                "rows": [{"metric": r[0], "actual": r[1], "minimum": r[2], "status": r[3]} for r in rows],
            },
            evidence=ToolEvidence(
                entity=entity.name,
                snapshot_date=str(snapshot.reporting_date),
                regulatory_refs=_REG_REFS,
                source_tables=_SOURCE_TABLES,
                confidence="HIGH",
            ),
            markdown="\n".join(md),
        )


class GenerateExecutiveSummaryTool(BaseTool):
    name = "generate_executive_summary"
    description = (
        "Generate a concise executive summary of the bank's regulatory capital "
        "and liquidity position. Suitable for C-suite briefings. "
        "Output is Markdown and includes key metrics, RAG status, and top watchpoints."
    )
    input_schema = {
        "type": "object",
        "properties": _ENTITY_SCHEMA,
        "required": ["entity_id"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        eid, sid, err = await _resolve_ids(params, db)
        if err:
            return self._error_result(err)

        entity, snapshot, lcr, nsfr, cap, bs = await _load_all(db, eid, sid)
        if not entity or not snapshot:
            return self._error_result("Entity or snapshot not found.")

        generated = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # RAG assessment
        lcr_rag = _rag(float(lcr.lcr_ratio) if lcr else None, (1.0, 1.3))
        nsfr_rag = _rag(float(nsfr.nsfr_ratio) if nsfr else None, (1.0, 1.2))
        cet1_rag = _rag(float(cap.cet1_ratio) if cap else None, (0.08, 0.10))
        lev_rag = _rag(float(cap.leverage_ratio) if cap else None, (0.035, 0.06))

        watchpoints = []
        if lcr and float(lcr.lcr_ratio) < 1.2:
            watchpoints.append("LCR approaching minimum — monitor HQLA composition and outflow run-off rates.")
        if nsfr and float(nsfr.nsfr_ratio) < 1.1:
            watchpoints.append("NSFR headroom below 10pp — consider term extension of wholesale liabilities.")
        if cap and float(cap.cet1_ratio) < 0.09:
            watchpoints.append("CET1 approaching CCB floor — restrict discretionary distributions.")
        if not watchpoints:
            watchpoints.append("No immediate regulatory concerns. Maintain current buffers.")

        md = [
            f"# Executive Summary — {entity.name}",
            f"**Reporting Date:** {snapshot.reporting_date} | **Generated:** {generated}",
            "",
            "## Overall Assessment",
            "",
            "### Liquidity Position",
            f"| LCR | {_pct(lcr.lcr_ratio if lcr else None)} | {lcr_rag} |",
            f"| NSFR | {_pct(nsfr.nsfr_ratio if nsfr else None)} | {nsfr_rag} |",
            "",
            "### Capital Position",
            f"| CET1 Ratio | {_pct(cap.cet1_ratio if cap else None)} | {cet1_rag} |",
            f"| Total Capital Ratio | {_pct(cap.total_capital_ratio if cap else None)} | — |",
            f"| Leverage Ratio | {_pct(cap.leverage_ratio if cap else None)} | {lev_rag} |",
            "",
            "### Balance Sheet",
            f"| Total Assets | {_num(bs.total_assets, bs.currency) if bs else 'N/A'} |",
            f"| Total Equity | {_num(bs.total_equity, bs.currency) if bs else 'N/A'} |",
            "",
            "## Watchpoints",
            *[f"- {w}" for w in watchpoints],
            "",
            f"*All figures computed by BSM deterministic engines. Snapshot: {snapshot.reporting_date}.*",
        ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={"entity": entity.name, "snapshot_date": str(snapshot.reporting_date)},
            evidence=ToolEvidence(
                entity=entity.name,
                snapshot_date=str(snapshot.reporting_date),
                regulatory_refs=_REG_REFS,
                source_tables=_SOURCE_TABLES,
                confidence="HIGH",
            ),
            markdown="\n".join(md),
        )


class GenerateBoardCommentaryTool(BaseTool):
    name = "generate_board_commentary"
    description = (
        "Generate board-ready risk commentary covering capital adequacy, liquidity risk, "
        "balance sheet health, and forward-looking watchpoints. "
        "Structured as a formal board paper section."
    )
    input_schema = {
        "type": "object",
        "properties": _ENTITY_SCHEMA,
        "required": ["entity_id"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        eid, sid, err = await _resolve_ids(params, db)
        if err:
            return self._error_result(err)

        entity, snapshot, lcr, nsfr, cap, bs = await _load_all(db, eid, sid)
        if not entity or not snapshot:
            return self._error_result("Entity or snapshot not found.")

        generated = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        md = [
            f"# Board Risk Commentary — {entity.name}",
            f"**Period Ended:** {snapshot.reporting_date} | **Prepared:** {generated}",
            f"**Classification:** BOARD CONFIDENTIAL",
            "",
            "## 1. Executive Risk Summary",
            f"As at {snapshot.reporting_date}, {entity.name} maintains "
            + ("adequate" if (lcr and float(lcr.lcr_ratio) >= 1.0 and cap and float(cap.cet1_ratio) >= 0.08) else "challenged")
            + " regulatory compliance across all Pillar 1 metrics. "
            "The following sections detail the position across each risk dimension.",
            "",
            "## 2. Liquidity Risk",
        ]

        if lcr:
            lcr_pct = float(lcr.lcr_ratio) * 100
            md += [
                f"**LCR:** {lcr_pct:.2f}% (minimum 100%). "
                f"{'Compliant with ' + str(lcr_pct - 100)[:5] + 'pp headroom.' if lcr_pct >= 100 else 'BELOW MINIMUM — immediate remediation required.'}",
                f"HQLA buffer of {_num(lcr.hqla_total, lcr.currency)} provides the liquidity backstop "
                f"against {_num(lcr.net_cash_outflows, lcr.currency)} net cash outflows over the 30-day stress horizon.",
            ]

        if nsfr:
            nsfr_pct = float(nsfr.nsfr_ratio) * 100
            surplus = float(nsfr.available_stable_funding) - float(nsfr.required_stable_funding)
            md += [
                "",
                f"**NSFR:** {nsfr_pct:.2f}% (minimum 100%). ASF surplus of {surplus:,.0f} {nsfr.currency} "
                "provides structural funding comfort over the 12-month horizon.",
            ]

        md += ["", "## 3. Capital Adequacy"]

        if cap:
            md += [
                f"**CET1 Ratio:** {_pct(cap.cet1_ratio)} vs. minimum 8.0% (incl. CCB). "
                f"Headroom: {(float(cap.cet1_ratio) - 0.08) * 100:.2f}pp.",
                f"**Total Capital Ratio:** {_pct(cap.total_capital_ratio)} vs. RBI minimum 10.875%.",
                f"**Leverage Ratio:** {_pct(cap.leverage_ratio)} vs. minimum 3.5%.",
                f"Total RWA: {_num(cap.total_rwa, cap.currency)}.",
            ]

        md += ["", "## 4. Balance Sheet"]

        if bs:
            leverage_mult = float(bs.total_assets) / float(bs.total_equity) if float(bs.total_equity) else 0
            md += [
                f"Total Assets: {_num(bs.total_assets, bs.currency)}",
                f"Total Equity: {_num(bs.total_equity, bs.currency)} (leverage multiple: {leverage_mult:.1f}×)",
                f"Off-Balance Sheet Exposures: {_num(bs.total_off_balance_sheet, bs.currency)}",
            ]

        md += [
            "",
            "## 5. Board Recommendations",
            "The Board is asked to note the regulatory compliance position "
            "and approve the following actions:",
            "1. Review and approve the Contingency Funding Plan quarterly update.",
            "2. Note the ICAAP capital assessment and buffer management strategy.",
            "3. Approve the regulatory reporting sign-off for the period.",
            "",
            "*All figures sourced from BSM Platform deterministic engines — audit trail available.*",
        ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={"entity": entity.name, "snapshot_date": str(snapshot.reporting_date)},
            evidence=ToolEvidence(
                entity=entity.name,
                snapshot_date=str(snapshot.reporting_date),
                regulatory_refs=_REG_REFS,
                source_tables=_SOURCE_TABLES,
                confidence="HIGH",
            ),
            markdown="\n".join(md),
        )


class GenerateCROCommentaryTool(BaseTool):
    name = "generate_cro_commentary"
    description = (
        "Generate Chief Risk Officer commentary on the bank's risk position. "
        "Covers all Pillar 1 metrics, stress resilience, and forward-looking "
        "risk watchpoints in CRO report style."
    )
    input_schema = {
        "type": "object",
        "properties": _ENTITY_SCHEMA,
        "required": ["entity_id"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        eid, sid, err = await _resolve_ids(params, db)
        if err:
            return self._error_result(err)

        entity, snapshot, lcr, nsfr, cap, bs = await _load_all(db, eid, sid)
        if not entity or not snapshot:
            return self._error_result("Entity or snapshot not found.")

        md = [
            f"# CRO Risk Commentary — {entity.name}",
            f"**Period:** {snapshot.reporting_date} | **Author:** Chief Risk Officer",
            "",
            "## Risk Dashboard",
            "",
            "| Risk Dimension | Key Metric | Value | RAG |",
            "|---|---|---|---|",
            f"| Liquidity (30-day) | LCR | {_pct(lcr.lcr_ratio if lcr else None)} | {_rag(float(lcr.lcr_ratio) if lcr else None, (1.0, 1.3))} |",
            f"| Liquidity (12-month) | NSFR | {_pct(nsfr.nsfr_ratio if nsfr else None)} | {_rag(float(nsfr.nsfr_ratio) if nsfr else None, (1.0, 1.2))} |",
            f"| Capital Adequacy | CET1 | {_pct(cap.cet1_ratio if cap else None)} | {_rag(float(cap.cet1_ratio) if cap else None, (0.08, 0.10))} |",
            f"| Capital (Total) | TCR | {_pct(cap.total_capital_ratio if cap else None)} | {_rag(float(cap.total_capital_ratio) if cap else None, (0.10875, 0.13))} |",
            f"| Leverage | Leverage Ratio | {_pct(cap.leverage_ratio if cap else None)} | {_rag(float(cap.leverage_ratio) if cap else None, (0.035, 0.06))} |",
            "",
            "## Liquidity Risk Assessment",
        ]

        if lcr:
            md += [
                f"The 30-day LCR of {_pct(lcr.lcr_ratio)} reflects an HQLA buffer of "
                f"{_num(lcr.hqla_total, lcr.currency)} against net cash outflows of "
                f"{_num(lcr.net_cash_outflows, lcr.currency)} under the Basel III stress scenario. "
                f"Inflow cap {'was' if lcr.inflow_cap_applied else 'was not'} binding.",
            ]

        if nsfr:
            surplus = float(nsfr.available_stable_funding) - float(nsfr.required_stable_funding)
            md += [
                f"Structural liquidity (NSFR) stands at {_pct(nsfr.nsfr_ratio)} with an ASF surplus "
                f"of {surplus:,.0f} {nsfr.currency}. No structural funding concern at this level.",
            ]

        md += ["", "## Capital Risk Assessment"]

        if cap:
            headroom_cet1 = (float(cap.cet1_ratio) - 0.08) * 100
            headroom_tcr = (float(cap.total_capital_ratio) - 0.10875) * 100
            md += [
                f"CET1 of {_pct(cap.cet1_ratio)} provides {headroom_cet1:.2f}pp headroom above the CCB floor. "
                f"Total Capital Ratio of {_pct(cap.total_capital_ratio)} gives {headroom_tcr:.2f}pp above RBI minimum.",
                f"RWA stands at {_num(cap.total_rwa, cap.currency)} "
                f"(Credit: {_pct(cap.rwa_credit / cap.total_rwa if cap.total_rwa else None)}, "
                f"Market: {_pct(cap.rwa_market / cap.total_rwa if cap.total_rwa else None)}, "
                f"Operational: {_pct(cap.rwa_operational / cap.total_rwa if cap.total_rwa else None)}).",
            ]

        md += [
            "",
            "## Top 3 Risk Watchpoints",
            "1. **Liquidity buffer adequacy**: Monitor HQLA composition for Level 2 concentration.",
            "2. **Capital buffer utilisation**: Track CET1 vs. stress RWA growth trajectory.",
            "3. **Funding concentration**: Review wholesale funding maturity profile quarterly.",
            "",
            "*CRO commentary is advisory only. All metrics from BSM Engine — not CRO estimates.*",
        ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={"entity": entity.name, "snapshot_date": str(snapshot.reporting_date)},
            evidence=ToolEvidence(
                entity=entity.name,
                snapshot_date=str(snapshot.reporting_date),
                regulatory_refs=_REG_REFS,
                source_tables=_SOURCE_TABLES,
                confidence="HIGH",
            ),
            markdown="\n".join(md),
        )


class GenerateCEOCommentaryTool(BaseTool):
    name = "generate_ceo_commentary"
    description = (
        "Generate a concise CEO brief on the bank's regulatory position. "
        "Non-technical language, forward-looking, suitable for external briefings."
    )
    input_schema = {
        "type": "object",
        "properties": _ENTITY_SCHEMA,
        "required": ["entity_id"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        eid, sid, err = await _resolve_ids(params, db)
        if err:
            return self._error_result(err)

        entity, snapshot, lcr, nsfr, cap, bs = await _load_all(db, eid, sid)
        if not entity or not snapshot:
            return self._error_result("Entity or snapshot not found.")

        all_pass = all([
            lcr and float(lcr.lcr_ratio) >= 1.0,
            nsfr and float(nsfr.nsfr_ratio) >= 1.0,
            cap and float(cap.cet1_ratio) >= 0.08,
            cap and float(cap.total_capital_ratio) >= 0.10875,
        ])

        md = [
            f"# CEO Brief — {entity.name}",
            f"**Period Ended:** {snapshot.reporting_date}",
            "",
            "## Regulatory Standing",
            f"{'All key Basel III regulatory metrics are within required limits.' if all_pass else 'One or more regulatory metrics require management attention.'} "
            f"The bank's liquidity coverage ratio of {_pct(lcr.lcr_ratio if lcr else None)} and "
            f"structural funding ratio of {_pct(nsfr.nsfr_ratio if nsfr else None)} confirm "
            "adequate short- and medium-term liquidity resilience.",
            "",
            "## Capital Strength",
            f"Core equity capital (CET1) stands at {_pct(cap.cet1_ratio if cap else None)}, "
            + (f"comfortably above the 8% minimum including the capital conservation buffer." if cap and float(cap.cet1_ratio) >= 0.08 else "approaching the minimum threshold."),
            "",
            "## Business Capacity",
        ]

        if bs:
            md += [
                f"The bank's total balance sheet of {_num(bs.total_assets, bs.currency)} "
                f"is supported by equity of {_num(bs.total_equity, bs.currency)}, "
                "providing a solid foundation for business growth within regulatory limits.",
            ]

        md += [
            "",
            "## Looking Ahead",
            "Management will continue to monitor regulatory ratios against internal risk appetite limits "
            "and report quarterly to the Board Risk Committee.",
            "",
            "*Based on BSM Platform engine results as at the period-end snapshot.*",
        ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={"entity": entity.name, "snapshot_date": str(snapshot.reporting_date)},
            evidence=ToolEvidence(
                entity=entity.name,
                snapshot_date=str(snapshot.reporting_date),
                regulatory_refs=_REG_REFS,
                source_tables=_SOURCE_TABLES,
                confidence="HIGH",
            ),
            markdown="\n".join(md),
        )


class GenerateICAAPSummaryTool(BaseTool):
    name = "generate_icaap_summary"
    description = (
        "Generate an ICAAP (Internal Capital Adequacy Assessment Process) summary section "
        "covering Pillar 2 capital requirements and stress testing commentary. "
        "Uses Pillar 1 metrics as the baseline for ICAAP assessment."
    )
    input_schema = {
        "type": "object",
        "properties": _ENTITY_SCHEMA,
        "required": ["entity_id"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        eid, sid, err = await _resolve_ids(params, db)
        if err:
            return self._error_result(err)

        entity, snapshot, lcr, nsfr, cap, bs = await _load_all(db, eid, sid)
        if not entity or not snapshot:
            return self._error_result("Entity or snapshot not found.")

        md = [
            f"# ICAAP Summary — {entity.name}",
            f"**Reference Period:** {snapshot.reporting_date}",
            "",
            "## Pillar 1 Baseline (from BSM Engines)",
            "",
            "| Metric | Actual | Pillar 1 Minimum |",
            "|---|---|---|",
        ]

        if cap:
            md += [
                f"| CET1 Ratio | {_pct(cap.cet1_ratio)} | 8.00% (incl. CCB) |",
                f"| Tier 1 Ratio | {_pct(cap.tier1_ratio)} | 6.00% |",
                f"| Total Capital Ratio | {_pct(cap.total_capital_ratio)} | 10.875% (RBI) |",
                f"| Leverage Ratio | {_pct(cap.leverage_ratio)} | 3.50% |",
                f"| Total RWA | {_num(cap.total_rwa, cap.currency)} | — |",
            ]

        md += [
            "",
            "## Pillar 2A Assessment",
            "The following additional capital requirements are assessed under Pillar 2A:",
            "- **Interest Rate Risk in Banking Book (IRRBB):** EVE sensitivity to parallel rate shock",
            "- **Concentration Risk:** Single-name and sector concentration in loan book",
            "- **Pension Risk:** Defined benefit pension scheme valuation sensitivity",
            "- **Operational Risk:** Internal loss data and external loss event overlay",
            "",
            "## ICAAP Capital Target",
        ]

        if cap:
            icaap_target = float(cap.cet1_ratio) + 0.02  # Illustrative P2A add-on
            md += [
                f"Pillar 1 CET1: {_pct(cap.cet1_ratio)}",
                f"Illustrative P2A Add-on: +200bps",
                f"ICAAP CET1 Target: {icaap_target * 100:.2f}% (indicative — subject to SREP determination)",
            ]

        md += [
            "",
            "## Stress Test Summary",
            "ICAAP stress tests are assessed using the BSM Stress Testing Engine. "
            "Results of the most recent scenario runs should be referenced from the "
            "Stress Test Summary report.",
            "",
            "**Applicable Regulatory Guidance:** RBI Pillar 2 ICAAP Guidance (2015); BCBS Supervisory Review Process (Jun 2011)",
            "",
            "*Note: This is an AI-generated ICAAP framework template. "
            "All Pillar 1 metrics sourced from BSM deterministic engines. "
            "Pillar 2A add-ons require expert judgment and SREP validation.*",
        ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={"entity": entity.name, "snapshot_date": str(snapshot.reporting_date)},
            evidence=ToolEvidence(
                entity=entity.name,
                snapshot_date=str(snapshot.reporting_date),
                regulatory_refs=[
                    "RBI ICAAP Guidance (2015)",
                    "BCBS Pillar 2 (Jun 2011)",
                    *_REG_REFS,
                ],
                source_tables=_SOURCE_TABLES,
                confidence="MEDIUM",
            ),
            markdown="\n".join(md),
        )


class GenerateILAAPSummaryTool(BaseTool):
    name = "generate_ilaap_summary"
    description = (
        "Generate an ILAAP (Internal Liquidity Adequacy Assessment Process) summary section "
        "covering LCR, NSFR, stress liquidity, and CFP (Contingency Funding Plan) commentary."
    )
    input_schema = {
        "type": "object",
        "properties": _ENTITY_SCHEMA,
        "required": ["entity_id"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        eid, sid, err = await _resolve_ids(params, db)
        if err:
            return self._error_result(err)

        entity, snapshot, lcr, nsfr, cap, bs = await _load_all(db, eid, sid)
        if not entity or not snapshot:
            return self._error_result("Entity or snapshot not found.")

        md = [
            f"# ILAAP Summary — {entity.name}",
            f"**Reference Period:** {snapshot.reporting_date}",
            "",
            "## 1. Liquidity Risk Overview",
            "The ILAAP assesses liquidity adequacy across three horizons: intraday, 30-day (LCR), "
            "and 12-month (NSFR). This summary covers the quantitative Basel III horizon assessments.",
            "",
            "## 2. 30-Day Liquidity Coverage Ratio",
        ]

        if lcr:
            md += [
                f"**LCR:** {_pct(lcr.lcr_ratio)} (minimum 100%) — {'COMPLIANT' if float(lcr.lcr_ratio) >= 1.0 else 'NON-COMPLIANT'}",
                f"**HQLA Buffer:** {_num(lcr.hqla_total, lcr.currency)}",
                f"**Net Cash Outflows:** {_num(lcr.net_cash_outflows, lcr.currency)}",
                f"**Inflow Cap Applied:** {'Yes — inflows capped at 75% of outflows' if lcr.inflow_cap_applied else 'No'}",
            ]

        md += ["", "## 3. 12-Month Net Stable Funding Ratio"]

        if nsfr:
            surplus = float(nsfr.available_stable_funding) - float(nsfr.required_stable_funding)
            md += [
                f"**NSFR:** {_pct(nsfr.nsfr_ratio)} (minimum 100%) — {'COMPLIANT' if float(nsfr.nsfr_ratio) >= 1.0 else 'NON-COMPLIANT'}",
                f"**Available Stable Funding (ASF):** {_num(nsfr.available_stable_funding, nsfr.currency)}",
                f"**Required Stable Funding (RSF):** {_num(nsfr.required_stable_funding, nsfr.currency)}",
                f"**ASF Surplus:** {surplus:,.2f} {nsfr.currency}",
            ]

        md += [
            "",
            "## 4. Liquidity Stress Assessment",
            "ILAAP stress scenarios are assessed using the BSM Stress Testing Engine. "
            "The three canonical stress scenarios are:",
            "| Scenario | LCR Impact | NSFR Impact |",
            "|---|---|---|",
            "| Mild (Base) | -5pp to -10pp | -3pp to -5pp |",
            "| Moderate (Adverse) | -15pp to -25pp | -10pp to -15pp |",
            "| Severe (Stressed) | -30pp to -50pp | -20pp to -30pp |",
            "(Actual stressed values: see Stress Test Summary report)",
            "",
            "## 5. Contingency Funding Plan (CFP)",
            "The CFP defines management actions available under each stress tier:",
            "- **Tier 1 (Early Warning):** LCR < 120% — activate liquidity monitoring committee",
            "- **Tier 2 (Stress):** LCR < 110% — drawdown committed facilities, restrict wholesale rollover",
            "- **Tier 3 (Crisis):** LCR < 100% — Central Bank Emergency Liquidity Assistance",
            "",
            "**Applicable Guidance:** BCBS LCR Monitoring Tools (Jan 2013); RBI LCR Master Circular",
            "",
            "*ILAAP template generated by BSM AI Copilot. All metrics sourced from BSM engines.*",
        ]

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={"entity": entity.name, "snapshot_date": str(snapshot.reporting_date)},
            evidence=ToolEvidence(
                entity=entity.name,
                snapshot_date=str(snapshot.reporting_date),
                regulatory_refs=[
                    "BCBS LCR Monitoring Tools (Jan 2013)",
                    "RBI LCR Master Circular (Jul 2015)",
                    "BCBS NSF20",
                    "RBI NSFR Guidelines (May 2018)",
                ],
                source_tables=["lcr_results", "nsfr_results"],
                confidence="MEDIUM",
            ),
            markdown="\n".join(md),
        )


class GenerateBasel3ComplianceTool(BaseTool):
    name = "generate_basel3_compliance"
    description = (
        "Generate a comprehensive Basel III compliance table covering all Pillar 1 metrics "
        "with actual values, minimums, headroom, and compliance status. "
        "Suitable for regulatory reporting and external audit."
    )
    input_schema = {
        "type": "object",
        "properties": _ENTITY_SCHEMA,
        "required": ["entity_id"],
    }

    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        eid, sid, err = await _resolve_ids(params, db)
        if err:
            return self._error_result(err)

        entity, snapshot, lcr, nsfr, cap, bs = await _load_all(db, eid, sid)
        if not entity or not snapshot:
            return self._error_result("Entity or snapshot not found.")

        generated = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        rows = []
        if lcr:
            lv = float(lcr.lcr_ratio)
            rows.append(("LCR", f"{lv * 100:.2f}%", "100.00%", f"+{(lv - 1.0) * 100:.2f}pp", "✅ PASS" if lv >= 1.0 else "❌ FAIL", "BCBS LCR30.40"))
        if nsfr:
            nv = float(nsfr.nsfr_ratio)
            rows.append(("NSFR", f"{nv * 100:.2f}%", "100.00%", f"+{(nv - 1.0) * 100:.2f}pp", "✅ PASS" if nv >= 1.0 else "❌ FAIL", "BCBS NSF20"))
        if cap:
            for key, label, minimum, ref in [
                ("cet1_ratio", "CET1 Ratio", 0.045, "BCBS CAP10"),
                ("tier1_ratio", "Tier 1 Ratio", 0.06, "BCBS CAP10"),
                ("total_capital_ratio", "Total Capital Ratio", 0.08, "BCBS CAP10"),
                ("leverage_ratio", "Leverage Ratio", 0.035, "BCBS LEV10"),
            ]:
                val = float(getattr(cap, key))
                headroom = (val - minimum) * 100
                rows.append((label, f"{val * 100:.2f}%", f"{minimum * 100:.2f}%", f"+{headroom:.2f}pp", "✅ PASS" if val >= minimum else "❌ FAIL", ref))

        # RBI enhanced minimums
        rbi_rows = []
        if cap:
            cet1 = float(cap.cet1_ratio)
            tcr = float(cap.total_capital_ratio)
            rbi_rows += [
                ("CET1 + CCB (RBI)", f"{cet1 * 100:.2f}%", "8.00%", f"+{(cet1 - 0.08) * 100:.2f}pp", "✅ PASS" if cet1 >= 0.08 else "❌ FAIL", "RBI Circular Jul 2015"),
                ("Total CRAR (RBI)", f"{tcr * 100:.2f}%", "10.875%", f"+{(tcr - 0.10875) * 100:.2f}pp", "✅ PASS" if tcr >= 0.10875 else "❌ FAIL", "RBI Circular Jul 2015"),
            ]

        md = [
            f"# Basel III Compliance Summary — {entity.name}",
            f"**Reporting Date:** {snapshot.reporting_date} | **Report Generated:** {generated}",
            "",
            "## Pillar 1 Compliance — Basel III Minimums",
            "",
            "| Metric | Actual | Basel III Min | Headroom | Status | Reference |",
            "|---|---|---|---|---|---|",
            *[f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |" for r in rows],
            "",
            "## Pillar 1 Compliance — RBI Enhanced Minimums",
            "",
            "| Metric | Actual | RBI Min | Headroom | Status | Reference |",
            "|---|---|---|---|---|---|",
            *[f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |" for r in rbi_rows],
            "",
            "## Certification",
            f"All figures computed by BSM deterministic engines as at {snapshot.reporting_date}. "
            "This report is auto-generated from the BSM Platform audit trail.",
            "",
            "*For regulatory submission, verify with the Finance / Compliance team.*",
        ]

        passes = [r[4] for r in rows + rbi_rows]
        all_pass = all("PASS" in p for p in passes)

        return ToolResult(
            success=True,
            tool_name=self.name,
            data={
                "entity": entity.name,
                "snapshot_date": str(snapshot.reporting_date),
                "all_pass": all_pass,
                "rows": [{"metric": r[0], "actual": r[1], "minimum": r[2], "headroom": r[3], "status": r[4]} for r in rows],
            },
            evidence=ToolEvidence(
                entity=entity.name,
                snapshot_date=str(snapshot.reporting_date),
                regulatory_refs=_REG_REFS,
                source_tables=_SOURCE_TABLES,
                confidence="HIGH",
            ),
            markdown="\n".join(md),
        )
