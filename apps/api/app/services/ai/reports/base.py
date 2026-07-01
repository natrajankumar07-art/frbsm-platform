"""Base types for AI-generated reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ReportType(str, Enum):
    EXECUTIVE_DASHBOARD = "executive_dashboard"
    DAILY_TREASURY = "daily_treasury"
    LIQUIDITY_RISK = "liquidity_risk"
    CAPITAL_ADEQUACY = "capital_adequacy"
    ALM_SUMMARY = "alm_summary"
    STRESS_TESTING = "stress_testing"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    BOARD_PACK = "board_pack"
    CRO_REPORT = "cro_report"
    CEO_BRIEF = "ceo_brief"

    @property
    def display_name(self) -> str:
        return {
            self.EXECUTIVE_DASHBOARD: "Executive Dashboard Summary",
            self.DAILY_TREASURY: "Daily Treasury Report",
            self.LIQUIDITY_RISK: "Liquidity Risk Report",
            self.CAPITAL_ADEQUACY: "Capital Adequacy Report",
            self.ALM_SUMMARY: "ALM Summary",
            self.STRESS_TESTING: "Stress Testing Summary",
            self.REGULATORY_COMPLIANCE: "Regulatory Compliance Summary",
            self.BOARD_PACK: "Board Pack",
            self.CRO_REPORT: "CRO Report",
            self.CEO_BRIEF: "CEO Brief",
        }[self]

    @property
    def description(self) -> str:
        return {
            self.EXECUTIVE_DASHBOARD: "High-level dashboard of all regulatory metrics with RAG status",
            self.DAILY_TREASURY: "Intraday and overnight liquidity position for treasury operations",
            self.LIQUIDITY_RISK: "Deep-dive LCR, NSFR, HQLA, and structural liquidity analysis",
            self.CAPITAL_ADEQUACY: "Full capital stack analysis: CET1, T1, TCR, Leverage, RWA breakdown",
            self.ALM_SUMMARY: "Asset-liability management summary: maturity profile, IRRBB, funding gaps",
            self.STRESS_TESTING: "Summary of stress test results across all available scenarios",
            self.REGULATORY_COMPLIANCE: "Basel III and RBI compliance table with headroom analysis",
            self.BOARD_PACK: "Consolidated board risk pack: all metrics + commentary + recommendations",
            self.CRO_REPORT: "Chief Risk Officer monthly risk report with watchpoints",
            self.CEO_BRIEF: "Executive CEO brief: plain language summary of regulatory position",
        }[self]


@dataclass
class Report:
    """A generated Markdown report with full provenance."""

    report_type: ReportType
    title: str
    entity: str
    snapshot_date: str
    generated_at: str
    content_markdown: str
    evidence: dict = field(default_factory=dict)
    export_hints: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "report_type": self.report_type.value,
            "title": self.title,
            "entity": self.entity,
            "snapshot_date": self.snapshot_date,
            "generated_at": self.generated_at,
            "content_markdown": self.content_markdown,
            "evidence": self.evidence,
            "export_hints": self.export_hints,
        }
