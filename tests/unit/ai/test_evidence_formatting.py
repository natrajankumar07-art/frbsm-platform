"""
Unit tests for the evidence citation utilities (Epic 4B).
"""

import pytest

from app.services.ai.evidence import (
    Citation,
    build_balance_sheet_citations,
    build_capital_citations,
    build_lcr_citations,
    build_nsfr_citations,
    format_citation,
)

ENTITY = "BSM Demo Bank Ltd"
DATE = "2026-03-31"

LCR_RAW = {
    "lcr_ratio": "1.5787",
    "hqla_total": "50000",
    "total_outflows": "40000",
    "total_inflows": "12000",
    "net_cash_outflows": "31681",
    "currency": "INR",
}

NSFR_RAW = {
    "nsfr_ratio": "1.2727",
    "available_stable_funding": "252000",
    "required_stable_funding": "198000",
    "currency": "INR",
}

CAPITAL_RAW = {
    "cet1_ratio": "0.1123",
    "tier1_ratio": "0.1283",
    "total_capital_ratio": "0.1605",
    "leverage_ratio": "0.0832",
    "cet1_capital": "36496.50",
    "total_rwa": "325000",
    "currency": "INR",
}

BS_RAW = {
    "total_assets": "325000",
    "total_liabilities": "292500",
    "total_equity": "32500",
    "off_balance_sheet": "15000",
    "currency": "INR",
}


# ── Citation dataclass ─────────────────────────────────────────────────────

class TestCitation:
    def test_can_construct(self):
        c = Citation(
            metric="LCR Ratio",
            value="157.87%",
            source="BSM LCR Engine v1.0.0",
            formula_ref="BCBS LCR30.40",
            entity=ENTITY,
            snapshot_date=DATE,
        )
        assert c.metric == "LCR Ratio"

    def test_format_citation_includes_all_fields(self):
        c = Citation(
            metric="LCR Ratio",
            value="157.87%",
            source="BSM LCR Engine v1.0.0",
            formula_ref="BCBS LCR30.40",
            entity=ENTITY,
            snapshot_date=DATE,
        )
        s = format_citation(c)
        assert "LCR Ratio" in s
        assert "157.87%" in s
        assert "BSM LCR Engine v1.0.0" in s
        assert "BCBS LCR30.40" in s
        assert ENTITY in s
        assert DATE in s


# ── LCR citations ──────────────────────────────────────────────────────────

class TestBuildLCRCitations:
    def test_returns_list_of_citations(self):
        result = build_lcr_citations(LCR_RAW, ENTITY, DATE)
        assert isinstance(result, list)
        assert all(isinstance(c, Citation) for c in result)

    def test_returns_five_citations(self):
        result = build_lcr_citations(LCR_RAW, ENTITY, DATE)
        assert len(result) == 5

    def test_first_citation_is_lcr_ratio(self):
        result = build_lcr_citations(LCR_RAW, ENTITY, DATE)
        assert result[0].metric == "LCR Ratio"

    def test_lcr_ratio_formatted_as_percent(self):
        result = build_lcr_citations(LCR_RAW, ENTITY, DATE)
        assert "%" in result[0].value
        assert "157.87" in result[0].value

    def test_hqla_citation_present(self):
        result = build_lcr_citations(LCR_RAW, ENTITY, DATE)
        metrics = [c.metric for c in result]
        assert "HQLA Total" in metrics

    def test_entity_and_date_set_on_all_citations(self):
        result = build_lcr_citations(LCR_RAW, ENTITY, DATE)
        for c in result:
            assert c.entity == ENTITY
            assert c.snapshot_date == DATE

    def test_source_references_bsm_engine(self):
        result = build_lcr_citations(LCR_RAW, ENTITY, DATE)
        for c in result:
            assert "BSM LCR Engine" in c.source

    def test_handles_missing_fields_gracefully(self):
        result = build_lcr_citations({}, ENTITY, DATE)
        assert len(result) == 5
        assert result[0].value == "N/A"


# ── NSFR citations ─────────────────────────────────────────────────────────

class TestBuildNSFRCitations:
    def test_returns_three_citations(self):
        result = build_nsfr_citations(NSFR_RAW, ENTITY, DATE)
        assert len(result) == 3

    def test_nsfr_ratio_is_first(self):
        result = build_nsfr_citations(NSFR_RAW, ENTITY, DATE)
        assert result[0].metric == "NSFR Ratio"

    def test_nsfr_ratio_formatted_as_percent(self):
        result = build_nsfr_citations(NSFR_RAW, ENTITY, DATE)
        assert "127.27" in result[0].value

    def test_asf_citation_present(self):
        result = build_nsfr_citations(NSFR_RAW, ENTITY, DATE)
        metrics = [c.metric for c in result]
        assert "Available Stable Funding (ASF)" in metrics

    def test_rsf_citation_present(self):
        result = build_nsfr_citations(NSFR_RAW, ENTITY, DATE)
        metrics = [c.metric for c in result]
        assert "Required Stable Funding (RSF)" in metrics


# ── Capital citations ──────────────────────────────────────────────────────

class TestBuildCapitalCitations:
    def test_returns_six_citations(self):
        result = build_capital_citations(CAPITAL_RAW, ENTITY, DATE)
        assert len(result) == 6

    def test_cet1_citation_present(self):
        result = build_capital_citations(CAPITAL_RAW, ENTITY, DATE)
        metrics = [c.metric for c in result]
        assert "CET1 Ratio" in metrics

    def test_leverage_ratio_citation_present(self):
        result = build_capital_citations(CAPITAL_RAW, ENTITY, DATE)
        metrics = [c.metric for c in result]
        assert "Leverage Ratio" in metrics

    def test_cet1_formatted_as_percent(self):
        result = build_capital_citations(CAPITAL_RAW, ENTITY, DATE)
        cet1 = next(c for c in result if c.metric == "CET1 Ratio")
        assert "11.23" in cet1.value

    def test_formula_ref_mentions_bcbs(self):
        result = build_capital_citations(CAPITAL_RAW, ENTITY, DATE)
        for c in result:
            assert "BCBS" in c.formula_ref or "RBI" in c.formula_ref


# ── Balance Sheet citations ────────────────────────────────────────────────

class TestBuildBalanceSheetCitations:
    def test_returns_four_citations(self):
        result = build_balance_sheet_citations(BS_RAW, ENTITY, DATE)
        assert len(result) == 4

    def test_total_assets_first(self):
        result = build_balance_sheet_citations(BS_RAW, ENTITY, DATE)
        assert result[0].metric == "Total Assets"

    def test_off_balance_sheet_present(self):
        result = build_balance_sheet_citations(BS_RAW, ENTITY, DATE)
        metrics = [c.metric for c in result]
        assert "Off-Balance Sheet Exposures" in metrics

    def test_values_include_currency(self):
        result = build_balance_sheet_citations(BS_RAW, ENTITY, DATE)
        for c in result:
            assert "INR" in c.value

    def test_source_references_bsm_engine(self):
        result = build_balance_sheet_citations(BS_RAW, ENTITY, DATE)
        for c in result:
            assert "BSM Balance Sheet Engine" in c.source
