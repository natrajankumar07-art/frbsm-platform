"""Unit tests for the NSFR engine."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from engines.common.models import NSFRAssetItem, NSFRFundingItem, NSFRInput
from engines.liquidity.nsfr import VERSION, compute_nsfr


def _simple_nsfr(asf: Decimal, rsf: Decimal) -> NSFRInput:
    return NSFRInput(
        snapshot_id="s",
        entity_id="e",
        reporting_date=date(2024, 3, 31),
        funding_items=[
            NSFRFundingItem(category="tier1_capital", balance=asf, asf_factor=Decimal("1.0"), maturity_bucket="gt_1y")
        ],
        asset_items=[
            NSFRAssetItem(category="other_assets", balance=rsf, rsf_factor=Decimal("1.0"), maturity_bucket="any")
        ],
        currency="INR",
    )


class TestNSFRBasicFormula:
    def test_nsfr_ratio_asf_over_rsf(self):
        result = compute_nsfr(_simple_nsfr(Decimal("120"), Decimal("100"))).result
        assert result.nsfr_ratio == Decimal("120.00000000") / Decimal("100.00000000")

    def test_passes_when_ratio_gte_1(self):
        result = compute_nsfr(_simple_nsfr(Decimal("100"), Decimal("100"))).result
        assert result.passes is True

    def test_fails_when_asf_less_than_rsf(self):
        result = compute_nsfr(_simple_nsfr(Decimal("80"), Decimal("100"))).result
        assert result.passes is False
        assert result.nsfr_ratio < Decimal("1")

    def test_asf_factors_applied(self):
        inp = NSFRInput(
            snapshot_id="s",
            entity_id="e",
            reporting_date=date(2024, 3, 31),
            funding_items=[
                NSFRFundingItem(category="retail_stable_lt1y", balance=Decimal("100"),
                                asf_factor=Decimal("0.95"), maturity_bucket="lt_6m"),
                NSFRFundingItem(category="tier1", balance=Decimal("10"),
                                asf_factor=Decimal("1.0"), maturity_bucket="gt_1y"),
            ],
            asset_items=[
                NSFRAssetItem(category="other", balance=Decimal("100"),
                              rsf_factor=Decimal("1.0"), maturity_bucket="any"),
            ],
        )
        result = compute_nsfr(inp).result
        # ASF = 100×0.95 + 10×1.0 = 105
        assert result.available_stable_funding == Decimal("105.00000000")

    def test_rsf_factors_applied(self):
        inp = NSFRInput(
            snapshot_id="s",
            entity_id="e",
            reporting_date=date(2024, 3, 31),
            funding_items=[
                NSFRFundingItem(category="tier1", balance=Decimal("500"),
                                asf_factor=Decimal("1.0"), maturity_bucket="gt_1y"),
            ],
            asset_items=[
                NSFRAssetItem(category="sovereign_l1", balance=Decimal("100"),
                              rsf_factor=Decimal("0.05"), maturity_bucket="any"),
                NSFRAssetItem(category="corporate_bonds_gt1y", balance=Decimal("50"),
                              rsf_factor=Decimal("0.5"), maturity_bucket="gt_1y"),
            ],
        )
        result = compute_nsfr(inp).result
        # RSF = 100×0.05 + 50×0.5 = 5 + 25 = 30
        assert result.required_stable_funding == Decimal("30.00000000")

    def test_version_constant(self):
        assert VERSION == "1.0.0"


class TestNSFRDeterminism:
    def test_same_inputs_identical_hashes(self):
        inp = _simple_nsfr(Decimal("200"), Decimal("150"))
        r1 = compute_nsfr(inp)
        r2 = compute_nsfr(inp)
        assert r1.trace.inputs_hash == r2.trace.inputs_hash
        assert r1.trace.outputs_hash == r2.trace.outputs_hash


class TestNSFRGoldenDemoBank:
    """
    Golden test using seeded BSM Demo Bank NSFR component data.
    The seeded database shows ASF=252,000 and RSF=198,000 (ratio=1.2727).

    ASF components (from nsfr_asf_components):
      retail_deposits_stable_gt1y:  80,000 × 0.95 = 76,000
      retail_term_deposits_gt1y:    45,000 × 0.95 = 42,750
      retail_deposits_stable_lt1y:  45,000 × 0.90 = 40,500
      retained_earnings:            40,000 × 1.00 = 40,000
      tier1_capital:                22,750 × 1.00 = 22,750
      retail_term_deposits_lt1y:    15,000 × 0.90 = 13,500
      tier2_capital_gt1y:            6,500 × 1.00 = 6,500
      corporate_non_op_deposits:    12,000 × 0.50 = 6,000
      corporate_op_deposits:         8,000 × 0.50 = 4,000
      repo_short_term:              10,000 × 0.00 = 0
      fi_deposits:                   4,000 × 0.00 = 0
      call_money:                    3,000 × 0.00 = 0
      Total ASF = 252,000

    RSF components (from nsfr_rsf_components):
      other_assets:                106,003 × 1.00 = 106,003
      loans_corporate_gt1y:         53,750 × 0.85 = 45,688 (rounded)
      loans_retail_hl_gt1y:         40,000 × 0.65 = 26,000
      hqla_level1_unencumbered:    130,400 × 0.05 = 6,520
      corporate_bonds_gt1y:          8,160 × 0.50 = 4,080
      loans_corporate_lt1y:          8,000 × 0.50 = 4,000
      cre_loans:                     1,450 × 1.00 = 1,450
      hqla_level2a:                  8,160 × 0.15 = 1,224
      loans_interbank_lt6m:          8,000 × 0.15 = 1,200
      loans_retail_hl_lt1y:          2,000 × 0.50 = 1,000
      loans_sme:                       700 × 0.85 = 595
      defaulted_exposures:             240 × 1.00 = 240
      Total RSF = 198,000
    """

    def _demo_input(self) -> NSFRInput:
        return NSFRInput(
            snapshot_id="d1000000-0000-0000-0000-000000000001",
            entity_id="a1000000-0000-0000-0000-000000000001",
            reporting_date=date(2026, 3, 31),
            funding_items=[
                NSFRFundingItem(category="retail_deposits_stable_gt1y", balance=Decimal("80000"),
                                asf_factor=Decimal("0.95"), maturity_bucket="gt_1y"),
                NSFRFundingItem(category="retail_term_deposits_gt1y", balance=Decimal("45000"),
                                asf_factor=Decimal("0.95"), maturity_bucket="gt_1y"),
                NSFRFundingItem(category="retail_deposits_stable_lt1y", balance=Decimal("45000"),
                                asf_factor=Decimal("0.90"), maturity_bucket="lt_6m"),
                NSFRFundingItem(category="retained_earnings", balance=Decimal("40000"),
                                asf_factor=Decimal("1.0"), maturity_bucket="gt_1y"),
                NSFRFundingItem(category="tier1_capital", balance=Decimal("22750"),
                                asf_factor=Decimal("1.0"), maturity_bucket="gt_1y"),
                NSFRFundingItem(category="retail_term_deposits_lt1y", balance=Decimal("15000"),
                                asf_factor=Decimal("0.90"), maturity_bucket="6m_1y"),
                NSFRFundingItem(category="tier2_capital_gt1y", balance=Decimal("6500"),
                                asf_factor=Decimal("1.0"), maturity_bucket="gt_1y"),
                NSFRFundingItem(category="corporate_non_op_deposits", balance=Decimal("12000"),
                                asf_factor=Decimal("0.50"), maturity_bucket="lt_6m"),
                NSFRFundingItem(category="corporate_op_deposits", balance=Decimal("8000"),
                                asf_factor=Decimal("0.50"), maturity_bucket="lt_6m"),
                NSFRFundingItem(category="repo_short_term", balance=Decimal("10000"),
                                asf_factor=Decimal("0.0"), maturity_bucket="lt_6m"),
                NSFRFundingItem(category="fi_deposits", balance=Decimal("4000"),
                                asf_factor=Decimal("0.0"), maturity_bucket="lt_6m"),
                NSFRFundingItem(category="call_money", balance=Decimal("3000"),
                                asf_factor=Decimal("0.0"), maturity_bucket="lt_6m"),
            ],
            asset_items=[
                NSFRAssetItem(category="other_assets", balance=Decimal("106003"),
                              rsf_factor=Decimal("1.0"), maturity_bucket="any"),
                NSFRAssetItem(category="loans_corporate_gt1y", balance=Decimal("53750"),
                              rsf_factor=Decimal("0.85"), maturity_bucket="gt_1y"),
                NSFRAssetItem(category="loans_retail_hl_gt1y", balance=Decimal("40000"),
                              rsf_factor=Decimal("0.65"), maturity_bucket="gt_1y"),
                NSFRAssetItem(category="hqla_level1_unencumbered", balance=Decimal("130400"),
                              rsf_factor=Decimal("0.05"), maturity_bucket="any"),
                NSFRAssetItem(category="corporate_bonds_gt1y", balance=Decimal("8160"),
                              rsf_factor=Decimal("0.50"), maturity_bucket="gt_1y"),
                NSFRAssetItem(category="loans_corporate_lt1y", balance=Decimal("8000"),
                              rsf_factor=Decimal("0.50"), maturity_bucket="lt_6m"),
                NSFRAssetItem(category="cre_loans", balance=Decimal("1450"),
                              rsf_factor=Decimal("1.0"), maturity_bucket="gt_1y"),
                NSFRAssetItem(category="hqla_level2a", balance=Decimal("8160"),
                              rsf_factor=Decimal("0.15"), maturity_bucket="any"),
                NSFRAssetItem(category="loans_interbank_lt6m", balance=Decimal("8000"),
                              rsf_factor=Decimal("0.15"), maturity_bucket="lt_6m"),
                NSFRAssetItem(category="loans_retail_hl_lt1y", balance=Decimal("2000"),
                              rsf_factor=Decimal("0.50"), maturity_bucket="lt_6m"),
                NSFRAssetItem(category="loans_sme", balance=Decimal("700"),
                              rsf_factor=Decimal("0.85"), maturity_bucket="gt_1y"),
                NSFRAssetItem(category="defaulted_exposures", balance=Decimal("240"),
                              rsf_factor=Decimal("1.0"), maturity_bucket="any"),
            ],
            currency="INR",
        )

    def test_asf_equals_252000(self):
        result = compute_nsfr(self._demo_input()).result
        assert result.available_stable_funding == Decimal("252000.00000000")

    def test_rsf_equals_197999_50(self):
        # 53,750 × 0.85 = 45,687.50 (exact Decimal); seeded DB stored 45,688 (rounded)
        # Engine is correct: actual sum = 197,999.50
        result = compute_nsfr(self._demo_input()).result
        assert result.required_stable_funding == Decimal("197999.50000000")

    def test_nsfr_ratio_approx_1_2727(self):
        result = compute_nsfr(self._demo_input()).result
        expected = Decimal("252000") / Decimal("198000")
        assert abs(result.nsfr_ratio - expected) < Decimal("0.0001")

    def test_passes(self):
        result = compute_nsfr(self._demo_input()).result
        assert result.passes is True
