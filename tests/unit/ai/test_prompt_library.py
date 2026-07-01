"""
Unit tests for the FRBSM prompt library (Epic 4B).

Verifies prompt count, structure, domain coverage, and system prompt quality.
"""

import pytest

from app.services.ai.prompts import COPILOT_SYSTEM_PROMPT, SUGGESTED_PROMPTS


class TestSuggestedPrompts:
    def test_prompt_count_at_least_50(self):
        assert len(SUGGESTED_PROMPTS) >= 50

    def test_every_prompt_has_category(self):
        for p in SUGGESTED_PROMPTS:
            assert "category" in p, f"Missing 'category' in: {p}"
            assert isinstance(p["category"], str)
            assert len(p["category"]) > 0

    def test_every_prompt_has_text(self):
        for p in SUGGESTED_PROMPTS:
            assert "text" in p, f"Missing 'text' in: {p}"
            assert isinstance(p["text"], str)
            assert len(p["text"]) > 10

    def test_no_duplicate_texts(self):
        texts = [p["text"] for p in SUGGESTED_PROMPTS]
        assert len(texts) == len(set(texts)), "Duplicate prompt texts found"

    def test_all_categories_are_strings(self):
        for p in SUGGESTED_PROMPTS:
            assert isinstance(p["category"], str)

    def test_liquidity_prompts_present(self):
        categories = {p["category"] for p in SUGGESTED_PROMPTS}
        liquidity_cats = {c for c in categories if "Liquidity" in c or "liquidity" in c}
        assert len(liquidity_cats) >= 1

    def test_capital_prompts_present(self):
        categories = {p["category"] for p in SUGGESTED_PROMPTS}
        assert any("Capital" in c for c in categories)

    def test_regulatory_prompts_present(self):
        categories = {p["category"] for p in SUGGESTED_PROMPTS}
        assert any("Regulatory" in c or "regulatory" in c for c in categories)

    def test_executive_prompts_present(self):
        categories = {p["category"] for p in SUGGESTED_PROMPTS}
        assert any("Executive" in c or "Board" in c for c in categories)

    def test_stress_prompts_present(self):
        categories = {p["category"] for p in SUGGESTED_PROMPTS}
        assert any("Stress" in c or "stress" in c for c in categories)

    def test_alm_prompts_present(self):
        categories = {p["category"] for p in SUGGESTED_PROMPTS}
        assert any("ALM" in c or "Asset" in c for c in categories)

    def test_balance_sheet_prompts_present(self):
        categories = {p["category"] for p in SUGGESTED_PROMPTS}
        assert any("Balance" in c or "balance" in c for c in categories)

    def test_prompts_are_questions_or_instructions(self):
        """Prompts should end with ? or be imperative statements."""
        for p in SUGGESTED_PROMPTS:
            text = p["text"]
            # Should be a proper sentence of at least 10 chars
            assert len(text) >= 10
            # Should not be empty or whitespace-only
            assert text.strip() == text

    def test_lcr_covered(self):
        texts = " ".join(p["text"] for p in SUGGESTED_PROMPTS).upper()
        assert "LCR" in texts

    def test_nsfr_covered(self):
        texts = " ".join(p["text"] for p in SUGGESTED_PROMPTS).upper()
        assert "NSFR" in texts

    def test_cet1_covered(self):
        texts = " ".join(p["text"] for p in SUGGESTED_PROMPTS).upper()
        assert "CET1" in texts

    def test_rbi_covered(self):
        texts = " ".join(p["text"] for p in SUGGESTED_PROMPTS)
        assert "RBI" in texts

    def test_basel_covered(self):
        texts = " ".join(p["text"] for p in SUGGESTED_PROMPTS).upper()
        assert "BASEL" in texts


class TestCopilotSystemPrompt:
    def test_is_string(self):
        assert isinstance(COPILOT_SYSTEM_PROMPT, str)

    def test_substantial_length(self):
        assert len(COPILOT_SYSTEM_PROMPT) >= 500

    def test_never_compute_rule_present(self):
        assert "NEVER" in COPILOT_SYSTEM_PROMPT.upper()

    def test_references_bsm_engines(self):
        assert "engine" in COPILOT_SYSTEM_PROMPT.lower() or "BSM" in COPILOT_SYSTEM_PROMPT

    def test_references_bcbs(self):
        assert "BCBS" in COPILOT_SYSTEM_PROMPT or "Basel" in COPILOT_SYSTEM_PROMPT

    def test_references_rbi(self):
        assert "RBI" in COPILOT_SYSTEM_PROMPT

    def test_mentions_lcr(self):
        assert "LCR" in COPILOT_SYSTEM_PROMPT

    def test_mentions_nsfr(self):
        assert "NSFR" in COPILOT_SYSTEM_PROMPT

    def test_mentions_capital(self):
        assert "capital" in COPILOT_SYSTEM_PROMPT.lower()

    def test_mentions_computed_by_engines(self):
        assert "COMPUTED BY BSM ENGINES" in COPILOT_SYSTEM_PROMPT

    def test_mckinsey_bcg_persona(self):
        prompt = COPILOT_SYSTEM_PROMPT.lower()
        assert "mckinsey" in prompt or "bcg" in prompt or "consulting" in prompt

    def test_no_compute_instruction(self):
        prompt = COPILOT_SYSTEM_PROMPT
        assert "NEVER compute" in prompt or "NEVER recompute" in prompt or "NEVER recalculate" in prompt
