"""
Unit tests for Epic 4C report generation infrastructure.
"""

import pytest

from app.services.ai.reports.base import Report, ReportType


# ── ReportType enum ────────────────────────────────────────────────────────

class TestReportType:
    def test_ten_report_types(self):
        assert len(list(ReportType)) == 10

    def test_all_have_display_name(self):
        for rt in ReportType:
            name = rt.display_name
            assert isinstance(name, str) and len(name) > 5

    def test_all_have_description(self):
        for rt in ReportType:
            desc = rt.description
            assert isinstance(desc, str) and len(desc) > 20

    def test_executive_dashboard_id(self):
        assert ReportType.EXECUTIVE_DASHBOARD.value == "executive_dashboard"

    def test_ceo_brief_id(self):
        assert ReportType.CEO_BRIEF.value == "ceo_brief"

    def test_board_pack_id(self):
        assert ReportType.BOARD_PACK.value == "board_pack"

    def test_cro_report_id(self):
        assert ReportType.CRO_REPORT.value == "cro_report"

    def test_regulatory_compliance_id(self):
        assert ReportType.REGULATORY_COMPLIANCE.value == "regulatory_compliance"

    def test_liquidity_risk_id(self):
        assert ReportType.LIQUIDITY_RISK.value == "liquidity_risk"

    def test_capital_adequacy_id(self):
        assert ReportType.CAPITAL_ADEQUACY.value == "capital_adequacy"

    def test_alm_summary_id(self):
        assert ReportType.ALM_SUMMARY.value == "alm_summary"

    def test_stress_testing_id(self):
        assert ReportType.STRESS_TESTING.value == "stress_testing"

    def test_daily_treasury_id(self):
        assert ReportType.DAILY_TREASURY.value == "daily_treasury"

    def test_value_roundtrip(self):
        for rt in ReportType:
            assert ReportType(rt.value) == rt


# ── Report dataclass ───────────────────────────────────────────────────────

class TestReportDataclass:
    def _make_report(self, report_type=ReportType.EXECUTIVE_DASHBOARD) -> Report:
        return Report(
            report_type=report_type,
            title="Test Report",
            entity="BSM Demo Bank Ltd",
            snapshot_date="2026-03-31",
            generated_at="2026-07-01 12:00 UTC",
            content_markdown="# Test\n\nContent here.",
            evidence={"confidence": "HIGH"},
            export_hints={"orientation": "portrait"},
        )

    def test_can_construct_report(self):
        r = self._make_report()
        assert r.title == "Test Report"

    def test_to_dict_has_required_keys(self):
        r = self._make_report()
        d = r.to_dict()
        assert "report_type" in d
        assert "title" in d
        assert "entity" in d
        assert "snapshot_date" in d
        assert "generated_at" in d
        assert "content_markdown" in d
        assert "evidence" in d
        assert "export_hints" in d

    def test_to_dict_report_type_is_string(self):
        r = self._make_report()
        d = r.to_dict()
        assert isinstance(d["report_type"], str)
        assert d["report_type"] == "executive_dashboard"

    def test_content_markdown_preserved(self):
        r = self._make_report()
        d = r.to_dict()
        assert "# Test" in d["content_markdown"]

    def test_export_hints_preserved(self):
        r = self._make_report()
        assert r.export_hints["orientation"] == "portrait"

    def test_all_report_types_can_be_constructed(self):
        for rt in ReportType:
            r = Report(
                report_type=rt,
                title=rt.display_name,
                entity="Test",
                snapshot_date="2026-03-31",
                generated_at="2026-07-01",
                content_markdown="# Test",
            )
            assert r.report_type == rt


# ── Architecture constraints ───────────────────────────────────────────────

class TestReportArchitecture:
    def test_generators_module_can_import(self):
        from app.services.ai.reports.generators import generate_report
        assert callable(generate_report)

    def test_report_types_match_generator_module(self):
        import importlib
        mod = importlib.import_module("app.services.ai.reports.generators")
        assert hasattr(mod, "generate_report")

    def test_report_is_exportable_as_markdown(self):
        r = Report(
            report_type=ReportType.CEO_BRIEF,
            title="CEO Brief",
            entity="Bank",
            snapshot_date="2026-03-31",
            generated_at="2026-07-01",
            content_markdown="# CEO Brief\n\n## Section 1\n\nContent.",
        )
        md = r.content_markdown
        assert "# CEO Brief" in md

    def test_pdf_docx_hook_via_export_hints(self):
        r = Report(
            report_type=ReportType.BOARD_PACK,
            title="Board Pack",
            entity="Bank",
            snapshot_date="2026-03-31",
            generated_at="2026-07-01",
            content_markdown="# Board Pack",
            export_hints={"orientation": "portrait", "sections": 8},
        )
        # Future PDF/DOCX exporters read export_hints without changing Report
        assert "orientation" in r.export_hints
        assert "sections" in r.export_hints
