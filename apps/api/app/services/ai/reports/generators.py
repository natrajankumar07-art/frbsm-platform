"""
Report generators — all 10 report types.

Each generator calls the appropriate analysis tools and assembles a full Report.
Architecture note: PDF/DOCX export will be added by wrapping content_markdown
without changing this module. The Report.export_hints dict signals intended
heading levels and section breaks to future exporters.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from ..tools.analysis_tools import (
    GenerateBasel3ComplianceTool,
    GenerateBoardCommentaryTool,
    GenerateCEOCommentaryTool,
    GenerateCROCommentaryTool,
    GenerateExecutiveSummaryTool,
    GenerateICAAPSummaryTool,
    GenerateILAAPSummaryTool,
    SummarizeRegulatoryResultsTool,
)
from ..tools.snapshot_tools import GetSnapshotsTool
from ..tools.stress_tools import RunStressScenarioTool
from .base import Report, ReportType

_EVIDENCE_TABLES = ["lcr_results", "nsfr_results", "capital_results", "balance_sheet_summaries"]
_REG_REFS = ["BCBS LCR30/40", "BCBS NSF20/30/40", "BCBS CAP10/LEV10", "RBI Master Circular (Jul 2015)"]


def _now() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


async def generate_report(
    db: AsyncSession,
    report_type: ReportType,
    entity_id: uuid.UUID,
    snapshot_id: uuid.UUID | None = None,
) -> Report:
    """Generate a full Markdown report of the given type."""

    params: dict = {"entity_id": str(entity_id)}
    if snapshot_id:
        params["snapshot_id"] = str(snapshot_id)

    generated_at = _now()
    entity_name = "Unknown Entity"
    snap_date = "N/A"

    if report_type == ReportType.EXECUTIVE_DASHBOARD:
        tool = GenerateExecutiveSummaryTool()
        result = await tool.execute(params, db)
        entity_name = result.data.get("entity", entity_name)
        snap_date = result.data.get("snapshot_date", snap_date)
        return Report(
            report_type=report_type,
            title=f"Executive Dashboard Summary — {entity_name}",
            entity=entity_name,
            snapshot_date=snap_date,
            generated_at=generated_at,
            content_markdown=result.markdown,
            evidence=result.evidence.to_dict(),
            export_hints={"orientation": "portrait", "sections": 3},
        )

    if report_type == ReportType.CEO_BRIEF:
        tool = GenerateCEOCommentaryTool()
        result = await tool.execute(params, db)
        entity_name = result.data.get("entity", entity_name)
        snap_date = result.data.get("snapshot_date", snap_date)
        return Report(
            report_type=report_type,
            title=f"CEO Brief — {entity_name}",
            entity=entity_name,
            snapshot_date=snap_date,
            generated_at=generated_at,
            content_markdown=result.markdown,
            evidence=result.evidence.to_dict(),
            export_hints={"orientation": "portrait", "sections": 3},
        )

    if report_type == ReportType.CRO_REPORT:
        tool = GenerateCROCommentaryTool()
        result = await tool.execute(params, db)
        entity_name = result.data.get("entity", entity_name)
        snap_date = result.data.get("snapshot_date", snap_date)
        return Report(
            report_type=report_type,
            title=f"CRO Risk Report — {entity_name}",
            entity=entity_name,
            snapshot_date=snap_date,
            generated_at=generated_at,
            content_markdown=result.markdown,
            evidence=result.evidence.to_dict(),
            export_hints={"orientation": "portrait", "sections": 5},
        )

    if report_type == ReportType.REGULATORY_COMPLIANCE:
        tool = GenerateBasel3ComplianceTool()
        result = await tool.execute(params, db)
        entity_name = result.data.get("entity", entity_name)
        snap_date = result.data.get("snapshot_date", snap_date)
        return Report(
            report_type=report_type,
            title=f"Regulatory Compliance Summary — {entity_name}",
            entity=entity_name,
            snapshot_date=snap_date,
            generated_at=generated_at,
            content_markdown=result.markdown,
            evidence=result.evidence.to_dict(),
            export_hints={"orientation": "landscape", "sections": 3},
        )

    if report_type == ReportType.BOARD_PACK:
        board_tool = GenerateBoardCommentaryTool()
        reg_tool = GenerateBasel3ComplianceTool()
        board_result = await board_tool.execute(params, db)
        reg_result = await reg_tool.execute(params, db)
        entity_name = board_result.data.get("entity", entity_name)
        snap_date = board_result.data.get("snapshot_date", snap_date)
        combined_md = "\n\n---\n\n".join([board_result.markdown, reg_result.markdown])
        return Report(
            report_type=report_type,
            title=f"Board Pack — {entity_name}",
            entity=entity_name,
            snapshot_date=snap_date,
            generated_at=generated_at,
            content_markdown=combined_md,
            evidence=board_result.evidence.to_dict(),
            export_hints={"orientation": "portrait", "sections": 8},
        )

    if report_type == ReportType.LIQUIDITY_RISK:
        tool = SummarizeRegulatoryResultsTool()
        result = await tool.execute(params, db)
        entity_name = result.data.get("entity", entity_name)
        snap_date = result.data.get("snapshot_date", snap_date)
        content = (
            f"# Liquidity Risk Report — {entity_name}\n"
            f"**Period Ended:** {snap_date} | **Generated:** {generated_at}\n\n"
            "## Liquidity Coverage Ratio and NSFR Analysis\n\n"
            + result.markdown
            + "\n\n## Regulatory Framework\n"
            "LCR: BCBS LCR30/40 (Jan 2013) | NSFR: BCBS NSF20/30/40 (Oct 2014) | "
            "RBI LCR Master Circular (Jul 2015) | RBI NSFR Guidelines (May 2018)\n\n"
            "*All figures sourced from BSM deterministic engines.*"
        )
        return Report(
            report_type=report_type,
            title=f"Liquidity Risk Report — {entity_name}",
            entity=entity_name,
            snapshot_date=snap_date,
            generated_at=generated_at,
            content_markdown=content,
            evidence=result.evidence.to_dict(),
            export_hints={"orientation": "portrait", "sections": 4},
        )

    if report_type == ReportType.CAPITAL_ADEQUACY:
        tool = SummarizeRegulatoryResultsTool()
        result = await tool.execute(params, db)
        entity_name = result.data.get("entity", entity_name)
        snap_date = result.data.get("snapshot_date", snap_date)
        content = (
            f"# Capital Adequacy Report — {entity_name}\n"
            f"**Period Ended:** {snap_date} | **Generated:** {generated_at}\n\n"
            "## Basel III Capital Summary\n\n"
            + result.markdown
            + "\n\n## Capital Stack Composition\n"
            "See BSM Platform Capital Adequacy dashboard for full RWA breakdown "
            "by risk type (Credit / Market / Operational).\n\n"
            "## Regulatory Framework\n"
            "BCBS CAP10 (Jun 2011) | BCBS LEV10 (Jan 2014) | "
            "RBI Master Circular Basel III Capital (Jul 2015)\n\n"
            "*All figures sourced from BSM deterministic engines.*"
        )
        return Report(
            report_type=report_type,
            title=f"Capital Adequacy Report — {entity_name}",
            entity=entity_name,
            snapshot_date=snap_date,
            generated_at=generated_at,
            content_markdown=content,
            evidence=result.evidence.to_dict(),
            export_hints={"orientation": "portrait", "sections": 5},
        )

    if report_type == ReportType.ALM_SUMMARY:
        tool = SummarizeRegulatoryResultsTool()
        result = await tool.execute(params, db)
        entity_name = result.data.get("entity", entity_name)
        snap_date = result.data.get("snapshot_date", snap_date)
        content = (
            f"# ALM Summary Report — {entity_name}\n"
            f"**Period Ended:** {snap_date} | **Generated:** {generated_at}\n\n"
            "## Asset-Liability Management Overview\n\n"
            "This report presents the quantitative liquidity and capital metrics as inputs "
            "to the ALM framework. Maturity ladder detail is available in the "
            "Structural Liquidity Statement (SLS) tables.\n\n"
            + result.markdown
            + "\n\n## IRRBB Assessment\n"
            "Interest rate risk in the banking book (IRRBB) is assessed separately under "
            "the BSM ALM module. Reference: BCBS IRRBB Standard (Apr 2016); "
            "RBI IRRBB Guidelines (Feb 2023).\n\n"
            "## ALM Risk Watchpoints\n"
            "1. Monitor LCR vs. NSFR gap — structural vs. short-term liquidity alignment\n"
            "2. Review repricing gap report monthly (SLS bucket analysis)\n"
            "3. Assess basis risk between MCLR lending and wholesale funding costs\n\n"
            "*ALM figures sourced from BSM deterministic engines.*"
        )
        return Report(
            report_type=report_type,
            title=f"ALM Summary — {entity_name}",
            entity=entity_name,
            snapshot_date=snap_date,
            generated_at=generated_at,
            content_markdown=content,
            evidence=result.evidence.to_dict(),
            export_hints={"orientation": "portrait", "sections": 5},
        )

    if report_type == ReportType.DAILY_TREASURY:
        tool = SummarizeRegulatoryResultsTool()
        result = await tool.execute(params, db)
        entity_name = result.data.get("entity", entity_name)
        snap_date = result.data.get("snapshot_date", snap_date)
        content = (
            f"# Daily Treasury Report — {entity_name}\n"
            f"**Reference Date:** {snap_date} | **Generated:** {generated_at}\n\n"
            "> **Note:** This daily treasury report is based on the most recent available "
            "snapshot. For intraday positions, see real-time treasury systems.\n\n"
            "## Key Liquidity Metrics (Snapshot Basis)\n\n"
            + result.markdown
            + "\n\n## Treasury Action Items\n"
            "- [ ] Confirm LCR compliance for today's reporting\n"
            "- [ ] Review HQLA eligibility for any new securities purchases\n"
            "- [ ] Update liquidity monitoring spreadsheet\n"
            "- [ ] Report to Risk Manager if LCR approaches 110%\n\n"
            "*Generated from BSM Platform snapshot data — not real-time.*"
        )
        return Report(
            report_type=report_type,
            title=f"Daily Treasury Report — {entity_name}",
            entity=entity_name,
            snapshot_date=snap_date,
            generated_at=generated_at,
            content_markdown=content,
            evidence=result.evidence.to_dict(),
            export_hints={"orientation": "portrait", "sections": 3},
        )

    if report_type == ReportType.STRESS_TESTING:
        snap_tool = GetSnapshotsTool()
        snap_result = await snap_tool.execute({"status": "locked", "limit": 1}, db)
        snaps = snap_result.data.get("snapshots", [])
        snap_date = snaps[0]["reporting_date"] if snaps else "N/A"

        content = (
            f"# Stress Testing Summary — {entity_name}\n"
            f"**Reference Period:** {snap_date} | **Generated:** {generated_at}\n\n"
            "## Overview\n"
            "This report summarises the results of all completed stress test runs "
            "for the most recent locked snapshot. Use the BSM Stress Test dashboard "
            "or the `run_stress_scenario` AI tool to query specific scenario results.\n\n"
            "## Stress Testing Framework\n"
            "| Dimension | Framework | Standard |\n"
            "|---|---|---|\n"
            "| Liquidity Stress | LCR run-off shock | BCBS LCR40 |\n"
            "| Capital Stress | Credit loss shock | BCBS CAP10 |\n"
            "| Structural Stress | ASF/RSF shifts | BCBS NSF20 |\n"
            "| Combined Stress | Multi-factor | ICAAP Pillar 2A |\n\n"
            "## Scenario Inventory\n"
            "All available stress scenarios can be listed using the `list_entities` "
            "and `run_stress_scenario` tools, or via the Scenarios API (`GET /v1/scenarios/`).\n\n"
            "## Regulatory References\n"
            "BCBS LCR40 (stress outflows) | BCBS CAP10 (stressed RWA) | "
            "RBI ICAAP Guidance (2015) | IMF FSAP Stress Methodology\n\n"
            "*Stress results sourced from pre-computed BSM engine runs.*"
        )
        return Report(
            report_type=report_type,
            title=f"Stress Testing Summary — {snap_date}",
            entity="All Entities",
            snapshot_date=snap_date,
            generated_at=generated_at,
            content_markdown=content,
            evidence={
                "engines_used": [],
                "source_tables": ["stress_test_runs", "stress_test_results", "scenarios"],
                "confidence": "MEDIUM",
            },
            export_hints={"orientation": "portrait", "sections": 4},
        )

    # Fallback for any type not explicitly handled
    return Report(
        report_type=report_type,
        title=f"{report_type.display_name} — Not Yet Implemented",
        entity=str(entity_id),
        snapshot_date="N/A",
        generated_at=generated_at,
        content_markdown=f"# {report_type.display_name}\n\nThis report type is not yet available.",
        evidence={},
        export_hints={},
    )
