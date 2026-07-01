"""
Unit tests for autonomous recommendation engine (Epic 6).
Tests: RecCategory, Recommendation, generate_recommendations.
No DB required — purely in-memory logic.
"""

import pytest

from app.services.ai.autonomous.recommendations import (
    RecCategory,
    Recommendation,
    generate_recommendations,
)


class TestRecCategory:
    def test_all_categories_exist(self):
        for c in ("LIQUIDITY", "CAPITAL", "FUNDING", "STRESS", "REGULATORY"):
            assert RecCategory[c] is not None

    def test_values_are_strings(self):
        assert isinstance(RecCategory.LIQUIDITY.value, str)


class TestGenerateRecommendations:
    def _base_kwargs(self, **overrides):
        base = dict(
            entity_name="Test Bank",
            entity_id=None,
            lcr_ratio=1.25,
            nsfr_ratio=1.15,
            cet1_ratio=0.12,
            tier1_ratio=0.14,
            total_capital_ratio=0.16,
            leverage_ratio=0.05,
            open_alert_count=0,
        )
        base.update(overrides)
        return base

    def test_returns_list(self):
        recs = generate_recommendations(**self._base_kwargs())
        assert isinstance(recs, list)

    def test_all_pass_few_recommendations(self):
        recs = generate_recommendations(**self._base_kwargs())
        # When all metrics pass, fewer / lower priority recommendations
        for r in recs:
            assert isinstance(r, Recommendation)

    def test_lcr_critical_produces_urgent_rec(self):
        recs = generate_recommendations(**self._base_kwargs(lcr_ratio=0.90))
        liquidity_recs = [r for r in recs if r.category == RecCategory.LIQUIDITY.value]
        assert len(liquidity_recs) > 0
        assert min(r.priority for r in liquidity_recs) <= 2

    def test_lcr_warning_produces_recommendation(self):
        recs = generate_recommendations(**self._base_kwargs(lcr_ratio=1.05))
        liquidity_recs = [r for r in recs if r.category == RecCategory.LIQUIDITY.value]
        assert len(liquidity_recs) > 0

    def test_cet1_breach_produces_capital_rec(self):
        recs = generate_recommendations(**self._base_kwargs(cet1_ratio=0.04))
        capital_recs = [r for r in recs if r.category == RecCategory.CAPITAL.value]
        assert len(capital_recs) > 0
        assert min(r.priority for r in capital_recs) <= 2

    def test_nsfr_breach_produces_funding_rec(self):
        recs = generate_recommendations(**self._base_kwargs(nsfr_ratio=0.95))
        funding_recs = [r for r in recs if r.category == RecCategory.FUNDING.value]
        assert len(funding_recs) > 0

    def test_high_alert_count_produces_regulatory_rec(self):
        recs = generate_recommendations(**self._base_kwargs(open_alert_count=5))
        regulatory_recs = [r for r in recs if r.category == RecCategory.REGULATORY.value]
        assert len(regulatory_recs) > 0

    def test_recommendation_fields_populated(self):
        recs = generate_recommendations(**self._base_kwargs(lcr_ratio=0.85))
        for rec in recs:
            assert rec.rec_id
            assert rec.title
            assert rec.description
            assert 1 <= rec.priority <= 5
            assert isinstance(rec.evidence, dict)

    def test_none_ratios_handled_gracefully(self):
        recs = generate_recommendations(**self._base_kwargs(
            lcr_ratio=None,
            nsfr_ratio=None,
            cet1_ratio=None,
            tier1_ratio=None,
            total_capital_ratio=None,
            leverage_ratio=None,
        ))
        assert isinstance(recs, list)

    def test_no_duplicate_titles(self):
        recs = generate_recommendations(**self._base_kwargs(lcr_ratio=0.85, cet1_ratio=0.04))
        titles = [r.title for r in recs]
        assert len(titles) == len(set(titles))
