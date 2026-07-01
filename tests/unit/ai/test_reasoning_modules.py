"""
Unit tests for Banking Intelligence reasoning modules (Epic 4B).

These tests verify module relevance logic and prompt extension generation
without any database or AI provider calls.
"""

import pytest

from app.services.ai.reasoning.alm import ALMModule
from app.services.ai.reasoning.balance_sheet import BalanceSheetModule
from app.services.ai.reasoning.base import ReasoningContext
from app.services.ai.reasoning.capital import CapitalModule
from app.services.ai.reasoning.executive import ExecutiveModule
from app.services.ai.reasoning.liquidity import LiquidityModule
from app.services.ai.reasoning.regulatory import RegulatoryModule
from app.services.ai.reasoning.stress import StressModule
from app.services.ai.reasoning_engine import (
    build_enriched_system_prompt,
    classify_intent,
)

# ── Fixtures ───────────────────────────────────────────────────────────────

LCR_DATA = {
    "lcr_ratio": "1.5787",
    "hqla_total": "50000",
    "total_outflows": "40000",
    "total_inflows": "12000",
    "net_cash_outflows": "31681",
    "minimum_ratio": "1.0",
    "passes": True,
    "inflow_cap_applied": False,
    "currency": "INR",
}

NSFR_DATA = {
    "nsfr_ratio": "1.2727",
    "available_stable_funding": "252000",
    "required_stable_funding": "198000",
    "minimum_ratio": "1.0",
    "passes": True,
    "currency": "INR",
}

CAPITAL_DATA = {
    "cet1_ratio": "0.1123",
    "tier1_ratio": "0.1283",
    "total_capital_ratio": "0.1605",
    "leverage_ratio": "0.0832",
    "cet1_capital": "36496.50",
    "additional_tier1": "5200",
    "tier2_capital": "10800",
    "total_capital": "52496.50",
    "total_rwa": "325000",
    "rwa_credit": "243750",
    "rwa_market": "48750",
    "rwa_operational": "32500",
    "passes_all": True,
    "currency": "INR",
}

BALANCE_SHEET_DATA = {
    "total_assets": "325000",
    "total_liabilities": "292500",
    "total_equity": "32500",
    "off_balance_sheet": "15000",
    "currency": "INR",
}


def _full_ctx(**overrides) -> ReasoningContext:
    defaults = dict(
        user_message="test",
        entity_name="BSM Demo Bank Ltd",
        snapshot_date="2026-03-31",
        lcr=LCR_DATA,
        nsfr=NSFR_DATA,
        capital=CAPITAL_DATA,
        balance_sheet=BALANCE_SHEET_DATA,
        detected_domains=["liquidity", "capital", "balance_sheet", "alm", "stress", "regulatory", "executive"],
    )
    defaults.update(overrides)
    return ReasoningContext(**defaults)


# ── Intent classification ──────────────────────────────────────────────────

class TestClassifyIntent:
    def test_lcr_keywords_map_to_liquidity(self):
        domains = classify_intent("What is our LCR ratio?")
        assert "liquidity" in domains

    def test_hqla_maps_to_liquidity(self):
        domains = classify_intent("Explain our HQLA buffer composition")
        assert "liquidity" in domains

    def test_nsfr_maps_to_liquidity(self):
        domains = classify_intent("What is the NSFR stable funding gap?")
        assert "liquidity" in domains

    def test_capital_keyword_maps_to_capital(self):
        domains = classify_intent("What is our CET1 ratio?")
        assert "capital" in domains

    def test_crar_maps_to_capital(self):
        domains = classify_intent("Explain our CRAR position")
        assert "capital" in domains

    def test_balance_sheet_maps_correctly(self):
        domains = classify_intent("Summarise the balance sheet total assets")
        assert "balance_sheet" in domains

    def test_alm_keywords_detected(self):
        domains = classify_intent("Discuss IRRBB and maturity mismatch")
        assert "alm" in domains

    def test_stress_keywords_detected(self):
        domains = classify_intent("Run an adverse stress test scenario")
        assert "stress" in domains

    def test_regulatory_keywords_detected(self):
        domains = classify_intent("RBI compliance and Basel pillar requirements")
        assert "regulatory" in domains

    def test_executive_keywords_detected(self):
        domains = classify_intent("Prepare a board summary overview")
        assert "executive" in domains

    def test_unknown_message_defaults_to_executive(self):
        domains = classify_intent("hello world")
        assert "executive" in domains

    def test_multi_domain_detection(self):
        msg = "LCR capital stress test regulatory RBI"
        domains = classify_intent(msg)
        assert len(domains) >= 3

    def test_returns_list_of_strings(self):
        domains = classify_intent("What is our LCR?")
        assert isinstance(domains, list)
        assert all(isinstance(d, str) for d in domains)


# ── Liquidity Module ───────────────────────────────────────────────────────

class TestLiquidityModule:
    module = LiquidityModule()

    def test_domain_is_liquidity(self):
        assert self.module.domain == "liquidity"

    def test_relevant_when_domain_detected(self):
        ctx = _full_ctx(detected_domains=["liquidity"])
        assert self.module.is_relevant(ctx)

    def test_relevant_when_lcr_data_present(self):
        ctx = _full_ctx(detected_domains=[], lcr=LCR_DATA)
        assert self.module.is_relevant(ctx)

    def test_not_relevant_without_data_or_domain(self):
        ctx = _full_ctx(detected_domains=[], lcr=None, nsfr=None)
        assert not self.module.is_relevant(ctx)

    def test_prompt_extension_is_string(self):
        ctx = _full_ctx(detected_domains=["liquidity"])
        ext = self.module.build_prompt_extension(ctx)
        assert isinstance(ext, str)
        assert len(ext) > 100

    def test_prompt_extension_mentions_lcr(self):
        ctx = _full_ctx(detected_domains=["liquidity"])
        ext = self.module.build_prompt_extension(ctx)
        assert "LCR" in ext

    def test_prompt_extension_includes_headroom(self):
        ctx = _full_ctx(detected_domains=["liquidity"])
        ext = self.module.build_prompt_extension(ctx)
        assert "headroom" in ext.lower() or "Headroom" in ext

    def test_prompt_extension_works_without_nsfr(self):
        ctx = _full_ctx(detected_domains=["liquidity"], nsfr=None)
        ext = self.module.build_prompt_extension(ctx)
        assert "LCR" in ext

    def test_prompt_extension_handles_none_lcr(self):
        ctx = _full_ctx(detected_domains=["liquidity"], lcr=None)
        ext = self.module.build_prompt_extension(ctx)
        assert isinstance(ext, str)


# ── Capital Module ─────────────────────────────────────────────────────────

class TestCapitalModule:
    module = CapitalModule()

    def test_domain_is_capital(self):
        assert self.module.domain == "capital"

    def test_relevant_when_domain_detected(self):
        ctx = _full_ctx(detected_domains=["capital"])
        assert self.module.is_relevant(ctx)

    def test_relevant_when_capital_data_present(self):
        ctx = _full_ctx(detected_domains=[], capital=CAPITAL_DATA)
        assert self.module.is_relevant(ctx)

    def test_not_relevant_without_data(self):
        ctx = _full_ctx(detected_domains=[], capital=None)
        assert not self.module.is_relevant(ctx)

    def test_prompt_mentions_cet1(self):
        ctx = _full_ctx(detected_domains=["capital"])
        ext = self.module.build_prompt_extension(ctx)
        assert "CET1" in ext

    def test_prompt_mentions_leverage(self):
        ctx = _full_ctx(detected_domains=["capital"])
        ext = self.module.build_prompt_extension(ctx)
        assert "Leverage" in ext or "leverage" in ext

    def test_prompt_includes_traffic_light_instruction(self):
        ctx = _full_ctx(detected_domains=["capital"])
        ext = self.module.build_prompt_extension(ctx)
        assert "traffic-light" in ext.lower() or "GREEN" in ext or "Red" in ext


# ── Balance Sheet Module ───────────────────────────────────────────────────

class TestBalanceSheetModule:
    module = BalanceSheetModule()

    def test_domain_is_balance_sheet(self):
        assert self.module.domain == "balance_sheet"

    def test_relevant_when_domain_detected(self):
        ctx = _full_ctx(detected_domains=["balance_sheet"])
        assert self.module.is_relevant(ctx)

    def test_relevant_when_bs_data_present(self):
        ctx = _full_ctx(detected_domains=[], balance_sheet=BALANCE_SHEET_DATA)
        assert self.module.is_relevant(ctx)

    def test_prompt_mentions_leverage_multiple(self):
        ctx = _full_ctx(detected_domains=["balance_sheet"])
        ext = self.module.build_prompt_extension(ctx)
        assert "leverage" in ext.lower() or "multiple" in ext.lower()

    def test_prompt_mentions_off_balance_sheet(self):
        ctx = _full_ctx(detected_domains=["balance_sheet"])
        ext = self.module.build_prompt_extension(ctx)
        assert "off-balance" in ext.lower() or "Off-Balance" in ext


# ── ALM Module ─────────────────────────────────────────────────────────────

class TestALMModule:
    module = ALMModule()

    def test_domain_is_alm(self):
        assert self.module.domain == "alm"

    def test_relevant_when_domain_detected(self):
        ctx = _full_ctx(detected_domains=["alm"])
        assert self.module.is_relevant(ctx)

    def test_relevant_when_both_lcr_and_nsfr_present(self):
        ctx = _full_ctx(detected_domains=[], lcr=LCR_DATA, nsfr=NSFR_DATA)
        assert self.module.is_relevant(ctx)

    def test_not_relevant_with_only_lcr(self):
        ctx = _full_ctx(detected_domains=[], lcr=LCR_DATA, nsfr=None)
        assert not self.module.is_relevant(ctx)

    def test_prompt_mentions_irrbb(self):
        ctx = _full_ctx(detected_domains=["alm"])
        ext = self.module.build_prompt_extension(ctx)
        assert "IRRBB" in ext

    def test_prompt_mentions_maturity_transformation(self):
        ctx = _full_ctx(detected_domains=["alm"])
        ext = self.module.build_prompt_extension(ctx)
        assert "maturity" in ext.lower()


# ── Stress Module ──────────────────────────────────────────────────────────

class TestStressModule:
    module = StressModule()

    def test_domain_is_stress(self):
        assert self.module.domain == "stress"

    def test_relevant_when_domain_detected(self):
        ctx = _full_ctx(detected_domains=["stress"])
        assert self.module.is_relevant(ctx)

    def test_not_relevant_by_data_alone(self):
        ctx = _full_ctx(detected_domains=[])
        assert not self.module.is_relevant(ctx)

    def test_prompt_mentions_adverse_scenario(self):
        ctx = _full_ctx(detected_domains=["stress"])
        ext = self.module.build_prompt_extension(ctx)
        assert "Adverse" in ext or "adverse" in ext

    def test_prompt_mentions_icaap(self):
        ctx = _full_ctx(detected_domains=["stress"])
        ext = self.module.build_prompt_extension(ctx)
        assert "ICAAP" in ext


# ── Regulatory Module ──────────────────────────────────────────────────────

class TestRegulatoryModule:
    module = RegulatoryModule()

    def test_domain_is_regulatory(self):
        assert self.module.domain == "regulatory"

    def test_relevant_when_regulatory_domain(self):
        ctx = _full_ctx(detected_domains=["regulatory"])
        assert self.module.is_relevant(ctx)

    def test_relevant_when_compliance_domain(self):
        ctx = _full_ctx(detected_domains=["compliance"])
        assert self.module.is_relevant(ctx)

    def test_prompt_mentions_rbi(self):
        ctx = _full_ctx(detected_domains=["regulatory"])
        ext = self.module.build_prompt_extension(ctx)
        assert "RBI" in ext

    def test_prompt_includes_compliance_table(self):
        ctx = _full_ctx(detected_domains=["regulatory"])
        ext = self.module.build_prompt_extension(ctx)
        assert "Compliance" in ext or "compliance" in ext


# ── Executive Module ───────────────────────────────────────────────────────

class TestExecutiveModule:
    module = ExecutiveModule()

    def test_domain_is_executive(self):
        assert self.module.domain == "executive"

    def test_relevant_when_executive_domain(self):
        ctx = _full_ctx(detected_domains=["executive"])
        assert self.module.is_relevant(ctx)

    def test_relevant_when_summary_in_domains(self):
        ctx = _full_ctx(detected_domains=["summary"])
        assert self.module.is_relevant(ctx)

    def test_prompt_mentions_board(self):
        ctx = _full_ctx(detected_domains=["executive"])
        ext = self.module.build_prompt_extension(ctx)
        assert "board" in ext.lower() or "Board" in ext

    def test_prompt_includes_traffic_light_values(self):
        ctx = _full_ctx(detected_domains=["executive"])
        ext = self.module.build_prompt_extension(ctx)
        assert "GREEN" in ext or "AMBER" in ext or "RED" in ext

    def test_indicative_lights_shown_when_data_present(self):
        ctx = _full_ctx(detected_domains=["executive"])
        ext = self.module.build_prompt_extension(ctx)
        assert "LCR" in ext or "NSFR" in ext or "CET1" in ext


# ── Enriched System Prompt ─────────────────────────────────────────────────

class TestBuildEnrichedSystemPrompt:
    BASE = "BASE_PROMPT_CONTENT"

    def test_returns_string(self):
        ctx = _full_ctx(detected_domains=["liquidity"])
        result = build_enriched_system_prompt(self.BASE, ctx)
        assert isinstance(result, str)

    def test_base_prompt_present_in_output(self):
        ctx = _full_ctx(detected_domains=["liquidity"])
        result = build_enriched_system_prompt(self.BASE, ctx)
        assert self.BASE in result

    def test_banking_intelligence_header_injected(self):
        ctx = _full_ctx(detected_domains=["liquidity"])
        result = build_enriched_system_prompt(self.BASE, ctx)
        assert "BANKING INTELLIGENCE LAYER" in result

    def test_activated_modules_listed(self):
        ctx = _full_ctx(detected_domains=["liquidity"])
        result = build_enriched_system_prompt(self.BASE, ctx)
        assert "LIQUIDITY" in result

    def test_no_modules_returns_base_prompt(self):
        ctx = ReasoningContext(
            user_message="hello",
            detected_domains=[],
            lcr=None,
            nsfr=None,
            capital=None,
            balance_sheet=None,
        )
        result = build_enriched_system_prompt(self.BASE, ctx)
        assert result == self.BASE

    def test_multiple_modules_all_contribute(self):
        ctx = _full_ctx(detected_domains=["liquidity", "capital", "executive"])
        result = build_enriched_system_prompt(self.BASE, ctx)
        assert "Liquidity Intelligence" in result
        assert "Capital Intelligence" in result
        assert "Executive Intelligence" in result

    def test_enriched_prompt_longer_than_base(self):
        ctx = _full_ctx(detected_domains=["liquidity", "capital"])
        result = build_enriched_system_prompt(self.BASE, ctx)
        assert len(result) > len(self.BASE)
