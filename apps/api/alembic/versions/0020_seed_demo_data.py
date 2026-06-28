"""Seed realistic demo banking data

Revision ID: 0020
Revises: 0019
Create Date: 2026-06-28

Inserts representative demo data for a mid-size Indian bank (BSM Demo Bank Ltd).
All monetary values are in INR crores (1 crore = 10 million INR).
Data reflects a month-end position as at 2026-03-31.

Reference:
  - Basel III risk weights: CRE20 (BIS, Dec 2017)
  - LCR run-off rates: LCR40 (BIS, Jan 2013)
  - NSFR factors: NSF20 (BIS, Oct 2014)
  - RBI capital requirements: Master Circular — Basel III Capital Regulations, 2023
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0020"
down_revision: str | None = "0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------
    # 1. Legal entities — BSM Demo Bank Ltd (consolidated + branches)
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO legal_entities
            (id, code, name, lei, entity_type, jurisdiction, regulator,
             license_type, is_consolidated, is_reporting_entity,
             functional_currency, created_at, updated_at)
        VALUES
        (
            'a1000000-0000-0000-0000-000000000001',
            'BSMDB', 'BSM Demo Bank Ltd',
            'BSMDBINBBXXX0000001',
            'bank', 'IN', 'RBI',
            'Scheduled Commercial Bank',
            true, true, 'INR',
            now(), now()
        ),
        (
            'a1000000-0000-0000-0000-000000000002',
            'BSMSG', 'BSM Demo Bank — Singapore Branch',
            NULL,
            'branch', 'IN', 'RBI',
            'Foreign Branch License',
            true, false, 'SGD',
            now(), now()
        )
    """))

    # ------------------------------------------------------------------
    # 2. Entity capital requirements — RBI minimums (India, 2023)
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO entity_capital_requirements
            (id, entity_id, requirement_type, minimum_ratio, buffer_requirement,
             effective_from, regulatory_reference, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'a1000000-0000-0000-0000-000000000001', 'CET1',     0.045, 0.025, '2023-04-01', 'RBI/2023-24/05 Master Circular — Basel III §3.1', now(), now()),
        (gen_random_uuid(), 'a1000000-0000-0000-0000-000000000001', 'Tier1',    0.060, 0.025, '2023-04-01', 'RBI/2023-24/05 Master Circular — Basel III §3.1', now(), now()),
        (gen_random_uuid(), 'a1000000-0000-0000-0000-000000000001', 'Total',    0.080, 0.025, '2023-04-01', 'RBI/2023-24/05 Master Circular — Basel III §3.1', now(), now()),
        (gen_random_uuid(), 'a1000000-0000-0000-0000-000000000001', 'Leverage', 0.035, 0.000, '2023-04-01', 'RBI/2023-24/05 Master Circular — Basel III §7.1', now(), now())
    """))

    # ------------------------------------------------------------------
    # 3. Product groups and products
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO product_groups (id, code, name, created_at, updated_at) VALUES
        ('b1000000-0000-0000-0000-000000000001', 'LOANS',   'Loans & Advances',       now(), now()),
        ('b1000000-0000-0000-0000-000000000002', 'DEPOSITS','Customer Deposits',       now(), now()),
        ('b1000000-0000-0000-0000-000000000003', 'INVEST',  'Investment Securities',   now(), now()),
        ('b1000000-0000-0000-0000-000000000004', 'BORROWS', 'Borrowings',              now(), now()),
        ('b1000000-0000-0000-0000-000000000005', 'DERIVS',  'Derivatives',             now(), now()),
        ('b1000000-0000-0000-0000-000000000006', 'OBS',     'Off-Balance-Sheet',       now(), now())
    """))

    conn.execute(sa.text("""
        INSERT INTO products
            (id, code, name, product_group_id, asset_class, instrument_type,
             basel_asset_class, lcr_eligible, nsfr_category, ifrs9_scope,
             is_active, created_at, updated_at)
        VALUES
        -- Loans
        ('b2000000-0000-0000-0000-000000000001', 'CORP_TL', 'Corporate Term Loan',      'b1000000-0000-0000-0000-000000000001', 'corporate',  'loan',   'corporate',   false, 'rsf_100',  true, true, now(), now()),
        ('b2000000-0000-0000-0000-000000000002', 'RETAIL_HL','Retail Home Loan',         'b1000000-0000-0000-0000-000000000001', 'residential_mortgage','loan','residential_mortgage',false,'rsf_65',  true, true, now(), now()),
        ('b2000000-0000-0000-0000-000000000003', 'SME_WC',  'SME Working Capital',       'b1000000-0000-0000-0000-000000000001', 'sme_corporate','loan',  'sme_corporate',false,'rsf_85',  true, true, now(), now()),
        ('b2000000-0000-0000-0000-000000000004', 'BANK_CL', 'Interbank Clean Loan',      'b1000000-0000-0000-0000-000000000001', 'bank',       'loan',   'bank',         false,'rsf_15',  true, true, now(), now()),
        -- Deposits
        ('b2000000-0000-0000-0000-000000000005', 'RETAIL_SA','Retail Savings Account',   'b1000000-0000-0000-0000-000000000002', 'retail',     'deposit','retail',       false,'asf_90',  false,true, now(), now()),
        ('b2000000-0000-0000-0000-000000000006', 'CORP_CA', 'Corporate Current Account', 'b1000000-0000-0000-0000-000000000002', 'corporate',  'deposit','corporate',    false,'asf_50',  false,true, now(), now()),
        ('b2000000-0000-0000-0000-000000000007', 'RETAIL_FD','Retail Fixed Deposit',     'b1000000-0000-0000-0000-000000000002', 'retail',     'deposit','retail',       false,'asf_95',  false,true, now(), now()),
        -- Securities
        ('b2000000-0000-0000-0000-000000000008', 'GOI_BOND','Govt of India Bond (HTM)',  'b1000000-0000-0000-0000-000000000003', 'sovereign',  'bond',   'sovereign',    true, 'rsf_5',   false,true, now(), now()),
        ('b2000000-0000-0000-0000-000000000009', 'TBILL',   'Treasury Bill',             'b1000000-0000-0000-0000-000000000003', 'sovereign',  'bond',   'sovereign',    true, 'rsf_5',   false,true, now(), now()),
        ('b2000000-0000-0000-0000-000000000010', 'CORP_BOND','Corporate Bond (AFS)',     'b1000000-0000-0000-0000-000000000003', 'corporate',  'bond',   'corporate',    false,'rsf_50',  false,true, now(), now()),
        -- Borrowings
        ('b2000000-0000-0000-0000-000000000011', 'CALL_MON','Call Money Borrowing',      'b1000000-0000-0000-0000-000000000004', 'bank',       'borrowing','bank',       false,'asf_0',   false,true, now(), now()),
        ('b2000000-0000-0000-0000-000000000012', 'REPO',    'Repo (Secured Borrowing)',  'b1000000-0000-0000-0000-000000000004', 'bank',       'repo',   'bank',         false,'asf_0',   false,true, now(), now())
    """))

    # ------------------------------------------------------------------
    # 4. Reference data — risk weights, HQLA haircuts, run-off rates,
    #    CCFs, yield curves
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO reference_risk_weights
            (id, asset_class, rating, jurisdiction, risk_weight,
             effective_from, regulatory_reference, created_at, updated_at)
        VALUES
        -- Sovereign (India) — 0% for claims on Indian Govt
        (gen_random_uuid(), 'sovereign', NULL, 'IN', 0.00, '2023-04-01', 'Basel III CRE20.27', now(), now()),
        -- Central bank — 0%
        (gen_random_uuid(), 'central_bank', NULL, 'IN', 0.00, '2023-04-01', 'Basel III CRE20.29', now(), now()),
        -- PSE (domestic) — 20%
        (gen_random_uuid(), 'pse', NULL, 'IN', 0.20, '2023-04-01', 'Basel III CRE20.32', now(), now()),
        -- MDB — 0% (eligible MDBs)
        (gen_random_uuid(), 'mdb', NULL, NULL, 0.00, '2023-04-01', 'Basel III CRE20.38', now(), now()),
        -- Bank claims — rated
        (gen_random_uuid(), 'bank', 'AAA',  NULL, 0.20, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        (gen_random_uuid(), 'bank', 'AA+',  NULL, 0.20, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        (gen_random_uuid(), 'bank', 'AA',   NULL, 0.20, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        (gen_random_uuid(), 'bank', 'AA-',  NULL, 0.20, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        (gen_random_uuid(), 'bank', 'A+',   NULL, 0.50, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        (gen_random_uuid(), 'bank', 'A',    NULL, 0.50, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        (gen_random_uuid(), 'bank', 'A-',   NULL, 0.50, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        (gen_random_uuid(), 'bank', 'BBB+', NULL, 1.00, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        (gen_random_uuid(), 'bank', 'BBB',  NULL, 1.00, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        (gen_random_uuid(), 'bank', 'BBB-', NULL, 1.00, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        (gen_random_uuid(), 'bank', 'UNRATED', NULL, 1.00, '2023-04-01', 'Basel III CRE20.46', now(), now()),
        -- Corporate — rated
        (gen_random_uuid(), 'corporate', 'AAA',    NULL, 0.20, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'AA+',    NULL, 0.20, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'AA',     NULL, 0.20, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'AA-',    NULL, 0.20, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'A+',     NULL, 0.50, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'A',      NULL, 0.50, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'A-',     NULL, 0.50, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'BBB+',   NULL, 1.00, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'BBB',    NULL, 1.00, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'BBB-',   NULL, 1.00, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'BB+',    NULL, 1.50, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'BB',     NULL, 1.50, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'BB-',    NULL, 1.50, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        (gen_random_uuid(), 'corporate', 'UNRATED',NULL, 1.00, '2023-04-01', 'Basel III CRE20.55', now(), now()),
        -- SME Corporate — 75% or 85%
        (gen_random_uuid(), 'sme_corporate', NULL, NULL, 0.85, '2023-04-01', 'Basel III CRE20.57', now(), now()),
        -- Retail (qualifying)
        (gen_random_uuid(), 'retail',    NULL, NULL, 0.75, '2023-04-01', 'Basel III CRE20.59', now(), now()),
        (gen_random_uuid(), 'sme_retail',NULL, NULL, 0.75, '2023-04-01', 'Basel III CRE20.62', now(), now()),
        -- Residential mortgage
        (gen_random_uuid(), 'residential_mortgage', NULL, NULL, 0.35, '2023-04-01', 'Basel III CRE20.69', now(), now()),
        -- Commercial real estate
        (gen_random_uuid(), 'commercial_real_estate', NULL, NULL, 1.00, '2023-04-01', 'Basel III CRE20.73', now(), now()),
        -- Equity
        (gen_random_uuid(), 'equity', NULL, NULL, 1.00, '2023-04-01', 'Basel III CRE20.83', now(), now()),
        -- Other assets
        (gen_random_uuid(), 'other', NULL, NULL, 1.00, '2023-04-01', 'Basel III CRE20.85', now(), now())
    """))

    conn.execute(sa.text("""
        INSERT INTO reference_hqla_haircuts
            (id, hqla_level, collateral_type, haircut, effective_from,
             regulatory_reference, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'level_1',  NULL,             0.00, '2023-04-01', 'Basel III LCR30.40', now(), now()),
        (gen_random_uuid(), 'level_1',  'sovereign_bond', 0.00, '2023-04-01', 'Basel III LCR30.40', now(), now()),
        (gen_random_uuid(), 'level_2a', NULL,             0.15, '2023-04-01', 'Basel III LCR30.42', now(), now()),
        (gen_random_uuid(), 'level_2a', 'corporate_bond', 0.15, '2023-04-01', 'Basel III LCR30.42', now(), now()),
        (gen_random_uuid(), 'level_2b', NULL,             0.25, '2023-04-01', 'Basel III LCR30.43', now(), now()),
        (gen_random_uuid(), 'level_2b', 'equity_listed',  0.50, '2023-04-01', 'Basel III LCR30.43', now(), now()),
        (gen_random_uuid(), 'ineligible',NULL,            0.00, '2023-04-01', 'Basel III LCR30',    now(), now())
    """))

    conn.execute(sa.text("""
        INSERT INTO reference_run_off_rates
            (id, deposit_type, customer_segment, run_off_rate, effective_from,
             regulatory_reference, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'retail_stable',            'retail',               0.03, '2023-04-01', 'Basel III LCR40.54', now(), now()),
        (gen_random_uuid(), 'retail_less_stable',       'retail',               0.10, '2023-04-01', 'Basel III LCR40.56', now(), now()),
        (gen_random_uuid(), 'small_business_stable',    'small_business',       0.05, '2023-04-01', 'Basel III LCR40.57', now(), now()),
        (gen_random_uuid(), 'small_business_less_stable','small_business',      0.10, '2023-04-01', 'Basel III LCR40.58', now(), now()),
        (gen_random_uuid(), 'operational_deposit',      'corporate',            0.25, '2023-04-01', 'Basel III LCR40.62', now(), now()),
        (gen_random_uuid(), 'non_operational_deposit_financial','financial_institution',0.40,'2023-04-01','Basel III LCR40.65',now(),now()),
        (gen_random_uuid(), 'non_operational_deposit_non_financial','corporate',0.40,'2023-04-01','Basel III LCR40.65',now(),now()),
        (gen_random_uuid(), 'unsecured_wholesale_financial','financial_institution',1.00,'2023-04-01','Basel III LCR40.68',now(),now()),
        (gen_random_uuid(), 'unsecured_wholesale_non_financial','corporate',    0.40, '2023-04-01', 'Basel III LCR40.68', now(), now()),
        (gen_random_uuid(), 'secured_funding',          'financial_institution',0.25, '2023-04-01', 'Basel III LCR40.69', now(), now())
    """))

    conn.execute(sa.text("""
        INSERT INTO reference_ccf
            (id, commitment_type, original_maturity_lt_1y, ccf, effective_from,
             regulatory_reference, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'unconditional_cancellable', NULL, 0.10, '2023-04-01', 'Basel III CRE20.93', now(), now()),
        (gen_random_uuid(), 'trade_finance_lt_1y',       true, 0.20, '2023-04-01', 'Basel III CRE20.94', now(), now()),
        (gen_random_uuid(), 'trade_finance_gt_1y',       false,0.50, '2023-04-01', 'Basel III CRE20.94', now(), now()),
        (gen_random_uuid(), 'note_issuance_facility',    NULL, 0.50, '2023-04-01', 'Basel III CRE20.96', now(), now()),
        (gen_random_uuid(), 'revolving_underwriting',    NULL, 0.50, '2023-04-01', 'Basel III CRE20.96', now(), now()),
        (gen_random_uuid(), 'other_commitment_lt_1y',    true, 0.20, '2023-04-01', 'Basel III CRE20.98', now(), now()),
        (gen_random_uuid(), 'other_commitment_gt_1y',    false,0.50, '2023-04-01', 'Basel III CRE20.98', now(), now()),
        (gen_random_uuid(), 'direct_credit_substitute',  NULL, 1.00, '2023-04-01', 'Basel III CRE20.95', now(), now())
    """))

    conn.execute(sa.text("""
        INSERT INTO reference_yield_curves
            (id, currency, curve_type, tenors_years, rates, as_of_date, created_at, updated_at)
        VALUES
        (
            gen_random_uuid(), 'INR', 'government',
            ARRAY[0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30],
            ARRAY[0.0655, 0.0663, 0.0670, 0.0678, 0.0685, 0.0695, 0.0703, 0.0714, 0.0725, 0.0731, 0.0740],
            '2026-03-31', now(), now()
        ),
        (
            gen_random_uuid(), 'INR', 'ois',
            ARRAY[0.25, 0.5, 1, 2, 3, 5, 7, 10],
            ARRAY[0.0645, 0.0650, 0.0655, 0.0660, 0.0665, 0.0672, 0.0680, 0.0690],
            '2026-03-31', now(), now()
        ),
        (
            gen_random_uuid(), 'USD', 'government',
            ARRAY[0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30],
            ARRAY[0.0525, 0.0530, 0.0518, 0.0490, 0.0475, 0.0460, 0.0452, 0.0445, 0.0440, 0.0438],
            '2026-03-31', now(), now()
        )
    """))

    # ------------------------------------------------------------------
    # 5. Counterparties
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO counterparties
            (id, name, lei, sector, industry, geography, jurisdiction,
             rating, is_financial_institution, is_sovereign, is_large_exposure,
             created_at, updated_at)
        VALUES
        -- Sovereign
        ('c1000000-0000-0000-0000-000000000001', 'Government of India', 'INDIANGOVTIND000001', 'sovereign', 'government', 'IN', 'IN', 'AAA', false, true, false, now(), now()),
        ('c1000000-0000-0000-0000-000000000002', 'Reserve Bank of India', 'RBIOFINBBXXX00001', 'central_bank', 'central_banking', 'IN', 'IN', 'AAA', true, false, false, now(), now()),
        -- Financial Institutions
        ('c1000000-0000-0000-0000-000000000003', 'State Bank of India', 'SBININBBXXX000001', 'bank', 'commercial_banking', 'IN', 'IN', 'AA', true, false, true, now(), now()),
        ('c1000000-0000-0000-0000-000000000004', 'HDFC Bank Ltd', 'HDFCINBBXXX00001', 'bank', 'commercial_banking', 'IN', 'IN', 'AA', true, false, false, now(), now()),
        ('c1000000-0000-0000-0000-000000000005', 'Citibank N.A. India', 'CITIINITXXX0001', 'bank', 'commercial_banking', 'IN', 'IN', 'AA-', true, false, false, now(), now()),
        -- Large Corporates
        ('c1000000-0000-0000-0000-000000000006', 'Reliance Industries Ltd', 'RELINDINBBXXX001', 'corporate', 'conglomerate', 'IN', 'IN', 'AAA', false, false, true, now(), now()),
        ('c1000000-0000-0000-0000-000000000007', 'Tata Consultancy Services Ltd', 'TCSINDINBBXXX01', 'corporate', 'technology', 'IN', 'IN', 'AA+', false, false, false, now(), now()),
        ('c1000000-0000-0000-0000-000000000008', 'Infosys Ltd', 'INFYINDINBBXXX1', 'corporate', 'technology', 'IN', 'IN', 'AA+', false, false, false, now(), now()),
        -- SME
        ('c1000000-0000-0000-0000-000000000009', 'Precision Engineering SME Pvt Ltd', NULL, 'sme_corporate', 'manufacturing', 'IN', 'IN', 'BBB', false, false, false, now(), now()),
        ('c1000000-0000-0000-0000-000000000010', 'Sunrise Foods & Beverages Pvt Ltd', NULL, 'sme_corporate', 'food_beverage', 'IN', 'IN', 'BB+', false, false, false, now(), now()),
        -- Retail (synthetic)
        ('c1000000-0000-0000-0000-000000000011', '[Retail Portfolio — Home Loans]', NULL, 'retail', 'retail_customers', 'IN', 'IN', 'UNRATED', false, false, false, now(), now()),
        ('c1000000-0000-0000-0000-000000000012', '[Retail Portfolio — Personal Loans]', NULL, 'retail', 'retail_customers', 'IN', 'IN', 'UNRATED', false, false, false, now(), now())
    """))

    # ------------------------------------------------------------------
    # 6. Snapshot — Q4 FY2026 (March 31, 2026)
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO snapshots
            (id, reporting_date, frozen_at, frozen_by, position_hash,
             reference_hash, position_count, status, notes, created_at, updated_at)
        VALUES (
            'd1000000-0000-0000-0000-000000000001',
            '2026-03-31',
            '2026-04-01 00:05:00+00',
            'system@bsm.demo',
            'a3f8c2e1b4d0f9a7c6e5b3d2a1f0e9c8b7d6a5f4e3d2c1b0a9f8e7d6c5b4a3f2',
            'b4a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0',
            30, 'locked',
            'Q4 FY2026 month-end snapshot. Demo data.',
            now(), now()
        )
    """))

    # ------------------------------------------------------------------
    # 7. Compute run — placeholder for balance sheet aggregation
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO compute_runs
            (id, snapshot_id, engine, function, version, git_sha,
             inputs_hash, outputs_hash, started_at, completed_at,
             duration_ms, success, created_at, updated_at)
        VALUES (
            'e1000000-0000-0000-0000-000000000001',
            'd1000000-0000-0000-0000-000000000001',
            'capital', 'compute_capital_adequacy', '1.0.0',
            '7274352a8b3c4d5e6f708192a3b4c5d6e7f80912',
            '1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b',
            '9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0',
            '2026-04-01 00:05:30+00',
            '2026-04-01 00:07:15+00',
            105000, true,
            now(), now()
        )
    """))

    # ------------------------------------------------------------------
    # 8. Positions — 30 representative balance sheet positions
    #    (amounts in INR crores)
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO positions
            (id, counterparty_id, product_code, currency, notional,
             booked_amount, fair_value, accrued_interest,
             maturity_date, repricing_date, behavioural_maturity,
             asset_class, credit_grade, ifrs9_stage, days_past_due,
             hqla_level, deposit_type, customer_segment,
             status, reporting_date, created_at, updated_at)
        VALUES
        -- Government Securities (HQLA Level 1)
        ('f1000000-0000-0000-0000-000000000001', 'c1000000-0000-0000-0000-000000000001', 'GOI_BOND', 'INR', 50000, 50250, 50250, 187.50, '2031-03-15', '2031-03-15', NULL, 'sovereign', 'AAA', 'stage_1', 0, 'level_1', NULL, NULL, 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000002', 'c1000000-0000-0000-0000-000000000001', 'GOI_BOND', 'INR', 30000, 30420, 30420, 120.00, '2029-09-22', '2029-09-22', NULL, 'sovereign', 'AAA', 'stage_1', 0, 'level_1', NULL, NULL, 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000003', 'c1000000-0000-0000-0000-000000000002', 'TBILL',    'INR', 20000, 19850, 19850, 0,      '2026-06-17', '2026-06-17', NULL, 'sovereign', 'AAA', 'stage_1', 0, 'level_1', NULL, NULL, 'active', '2026-03-31', now(), now()),
        -- Interbank Loans
        ('f1000000-0000-0000-0000-000000000004', 'c1000000-0000-0000-0000-000000000003', 'BANK_CL',  'INR', 5000,  5000,  5000,  8.33,   '2026-05-01', '2026-05-01', NULL, 'bank', 'AA', 'stage_1', 0, 'ineligible', NULL, 'financial_institution', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000005', 'c1000000-0000-0000-0000-000000000004', 'BANK_CL',  'INR', 3000,  3000,  3000,  6.25,   '2026-04-07', '2026-04-07', NULL, 'bank', 'AA', 'stage_1', 0, 'ineligible', NULL, 'financial_institution', 'active', '2026-03-31', now(), now()),
        -- Large Corporate Loans
        ('f1000000-0000-0000-0000-000000000006', 'c1000000-0000-0000-0000-000000000006', 'CORP_TL',  'INR', 25000, 24750, 24750, 103.13, '2030-03-31', '2027-03-31', NULL, 'corporate', 'AAA', 'stage_1', 0, 'ineligible', NULL, 'corporate', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000007', 'c1000000-0000-0000-0000-000000000007', 'CORP_TL',  'INR', 15000, 14850, 14850, 61.88,  '2028-09-30', '2026-09-30', NULL, 'corporate', 'AA+', 'stage_1', 0, 'ineligible', NULL, 'corporate', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000008', 'c1000000-0000-0000-0000-000000000008', 'CORP_TL',  'INR', 10000, 9900,  9900,  41.25,  '2027-12-31', '2026-12-31', NULL, 'corporate', 'AA+', 'stage_1', 0, 'ineligible', NULL, 'corporate', 'active', '2026-03-31', now(), now()),
        -- SME Loans
        ('f1000000-0000-0000-0000-000000000009', 'c1000000-0000-0000-0000-000000000009', 'SME_WC',   'INR', 500,   490,   490,   2.04,   '2026-09-30', '2026-09-30', NULL, 'sme_corporate', 'BBB', 'stage_1', 0, 'ineligible', NULL, 'corporate', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000010', 'c1000000-0000-0000-0000-000000000010', 'SME_WC',   'INR', 200,   185,   185,   0.77,   '2026-06-30', '2026-06-30', NULL, 'sme_corporate', 'BB+', 'stage_2', 15, 'ineligible', NULL, 'corporate', 'active', '2026-03-31', now(), now()),
        -- Retail Home Loans (portfolio, pooled under retail counterparty)
        ('f1000000-0000-0000-0000-000000000011', 'c1000000-0000-0000-0000-000000000011', 'RETAIL_HL','INR', 40000, 39200, 39200, 163.33, '2040-03-31', NULL, '2030-03-31', 'residential_mortgage', 'UNRATED', 'stage_1', 0, 'ineligible', NULL, 'retail', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000012', 'c1000000-0000-0000-0000-000000000011', 'RETAIL_HL','INR', 2000,  1900,  1900,  7.92,   '2035-12-31', NULL, '2029-12-31', 'residential_mortgage', 'UNRATED', 'stage_2', 45, 'ineligible', NULL, 'retail', 'active', '2026-03-31', now(), now()),
        -- Deposits (liabilities — negative fair_value convention for engines)
        ('f1000000-0000-0000-0000-000000000013', 'c1000000-0000-0000-0000-000000000011', 'RETAIL_SA','INR', 80000, 80000, 80000, 0,      NULL, NULL, NULL, 'retail', 'UNRATED', 'stage_1', 0, 'ineligible', 'retail_stable', 'retail', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000014', 'c1000000-0000-0000-0000-000000000012', 'RETAIL_SA','INR', 30000, 30000, 30000, 0,      NULL, NULL, NULL, 'retail', 'UNRATED', 'stage_1', 0, 'ineligible', 'retail_less_stable', 'retail', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000015', 'c1000000-0000-0000-0000-000000000006', 'CORP_CA',  'INR', 12000, 12000, 12000, 0,      NULL, NULL, NULL, 'corporate', 'AAA', 'stage_1', 0, 'ineligible', 'non_operational_deposit_non_financial', 'corporate', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000016', 'c1000000-0000-0000-0000-000000000007', 'CORP_CA',  'INR', 8000,  8000,  8000,  0,      NULL, NULL, NULL, 'corporate', 'AA+', 'stage_1', 0, 'ineligible', 'operational_deposit', 'corporate', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000017', 'c1000000-0000-0000-0000-000000000011', 'RETAIL_FD','INR', 45000, 45000, 45000, 0,      '2027-03-31', NULL, '2027-03-31', 'retail', 'UNRATED', 'stage_1', 0, 'ineligible', 'retail_stable', 'retail', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000018', 'c1000000-0000-0000-0000-000000000012', 'RETAIL_FD','INR', 15000, 15000, 15000, 0,      '2026-06-30', NULL, '2026-06-30', 'retail', 'UNRATED', 'stage_1', 0, 'ineligible', 'retail_less_stable', 'retail', 'active', '2026-03-31', now(), now()),
        -- Borrowings
        ('f1000000-0000-0000-0000-000000000019', 'c1000000-0000-0000-0000-000000000003', 'CALL_MON', 'INR', 3000,  3000,  3000,  1.25,   '2026-04-01', NULL, NULL, 'bank', 'AA', 'stage_1', 0, 'ineligible', 'non_operational_deposit_financial', 'financial_institution', 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000020', 'c1000000-0000-0000-0000-000000000002', 'REPO',     'INR', 10000, 10000, 10000, 18.49,  '2026-04-07', NULL, NULL, 'central_bank', 'AAA', 'stage_1', 0, 'ineligible', 'secured_funding', 'central_bank', 'active', '2026-03-31', now(), now()),
        -- Corporate bonds (AFS portfolio)
        ('f1000000-0000-0000-0000-000000000021', 'c1000000-0000-0000-0000-000000000006', 'CORP_BOND','INR', 5000,  5100,  5100,  31.25,  '2031-06-15', '2031-06-15', NULL, 'corporate', 'AAA', 'stage_1', 0, 'level_2a', NULL, NULL, 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000022', 'c1000000-0000-0000-0000-000000000007', 'CORP_BOND','INR', 3000,  3060,  3060,  18.75,  '2029-12-31', '2029-12-31', NULL, 'corporate', 'AA+', 'stage_1', 0, 'level_2a', NULL, NULL, 'active', '2026-03-31', now(), now()),
        -- Stage 3 (credit-impaired) position
        ('f1000000-0000-0000-0000-000000000023', 'c1000000-0000-0000-0000-000000000010', 'SME_WC',   'INR', 300,   240,   200,   0,      '2025-09-30', NULL, NULL, 'sme_corporate', 'BB-', 'stage_3', 120, 'ineligible', NULL, 'corporate', 'defaulted', '2026-03-31', now(), now()),
        -- Additional government securities
        ('f1000000-0000-0000-0000-000000000024', 'c1000000-0000-0000-0000-000000000001', 'GOI_BOND', 'INR', 20000, 20300, 20300, 80.00,  '2035-01-25', '2035-01-25', NULL, 'sovereign', 'AAA', 'stage_1', 0, 'level_1', NULL, NULL, 'active', '2026-03-31', now(), now()),
        ('f1000000-0000-0000-0000-000000000025', 'c1000000-0000-0000-0000-000000000001', 'GOI_BOND', 'INR', 10000, 10150, 10150, 40.00,  '2028-07-18', '2028-07-18', NULL, 'sovereign', 'AAA', 'stage_1', 0, 'level_1', NULL, NULL, 'active', '2026-03-31', now(), now()),
        -- PSE loan
        ('f1000000-0000-0000-0000-000000000026', 'c1000000-0000-0000-0000-000000000001', 'CORP_TL',  'INR', 8000,  7920,  7920,  33.00,  '2029-06-30', '2027-06-30', NULL, 'pse', 'AAA', 'stage_1', 0, 'ineligible', NULL, 'sovereign', 'active', '2026-03-31', now(), now()),
        -- Retail personal loans (higher risk)
        ('f1000000-0000-0000-0000-000000000027', 'c1000000-0000-0000-0000-000000000012', 'RETAIL_HL','INR', 5000,  4800,  4800,  20.00,  '2031-03-31', NULL, '2028-03-31', 'retail', 'UNRATED', 'stage_1', 0, 'ineligible', NULL, 'retail', 'active', '2026-03-31', now(), now()),
        -- Interbank deposit placed
        ('f1000000-0000-0000-0000-000000000028', 'c1000000-0000-0000-0000-000000000005', 'BANK_CL',  'INR', 2000,  2000,  2000,  4.17,   '2026-04-30', '2026-04-30', NULL, 'bank', 'AA-', 'stage_1', 0, 'ineligible', NULL, 'financial_institution', 'active', '2026-03-31', now(), now()),
        -- Additional FI deposit received
        ('f1000000-0000-0000-0000-000000000029', 'c1000000-0000-0000-0000-000000000003', 'CORP_CA',  'INR', 4000,  4000,  4000,  0,      NULL, NULL, NULL, 'bank', 'AA', 'stage_1', 0, 'ineligible', 'non_operational_deposit_financial', 'financial_institution', 'active', '2026-03-31', now(), now()),
        -- Commercial real estate loan
        ('f1000000-0000-0000-0000-000000000030', 'c1000000-0000-0000-0000-000000000009', 'CORP_TL',  'INR', 1500,  1450,  1420,  6.04,   '2028-12-31', '2027-12-31', NULL, 'commercial_real_estate', 'BBB', 'stage_1', 0, 'ineligible', NULL, 'corporate', 'active', '2026-03-31', now(), now())
    """))

    # ------------------------------------------------------------------
    # 9. Collateral on selected positions
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO collateral
            (id, position_id, position_reporting_date, collateral_type, description,
             market_value, currency, haircut, net_value, created_at, updated_at)
        VALUES
        -- Govt bond repo collateral
        (gen_random_uuid(), 'f1000000-0000-0000-0000-000000000020', '2026-03-31', 'sovereign_bond', 'GOI 7.18% 2033 — repo collateral', 10200, 'INR', 0.00, 10200, now(), now()),
        -- Home loan — residential property charge
        (gen_random_uuid(), 'f1000000-0000-0000-0000-000000000011', '2026-03-31', 'property_residential', 'Residential mortgage pool — equitable charge', 78400, 'INR', 0.20, 62720, now(), now()),
        -- Corporate loan — cash collateral
        (gen_random_uuid(), 'f1000000-0000-0000-0000-000000000006', '2026-03-31', 'cash', 'Cash margin account — Reliance Industries', 5000, 'INR', 0.00, 5000, now(), now()),
        -- CRE loan — property charge
        (gen_random_uuid(), 'f1000000-0000-0000-0000-000000000030', '2026-03-31', 'property_commercial', 'Commercial property — first charge', 2200, 'INR', 0.35, 1430, now(), now()),
        -- Defaulted SME — guarantor
        (gen_random_uuid(), 'f1000000-0000-0000-0000-000000000023', '2026-03-31', 'guarantee', 'Director personal guarantee — Sunrise Foods', 150, 'INR', 0.00, 150, now(), now())
    """))

    # ------------------------------------------------------------------
    # 10. Scenarios
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO scenarios
            (id, code, name, description, scenario_type, severity,
             is_regulatory, regulatory_reference, is_active, created_by,
             created_at, updated_at)
        VALUES
        (
            'a2000000-0000-0000-0000-000000000001',
            'BASE_CASE', 'Base Case — No Stress',
            'Business-as-usual scenario with current market conditions.',
            'base', NULL, false, NULL, true, 'system@bsm.demo',
            now(), now()
        ),
        (
            'a2000000-0000-0000-0000-000000000002',
            'RBI_SEVERE', 'RBI Severe Stress Scenario — FY2026',
            'Regulatory severe stress: 300bps parallel rate shock, 20% credit migration, 40% equity decline. Per RBI SREP guidelines.',
            'regulatory', 'severe', true, 'RBI/2025-26/SREP Circular §4.2', true, 'risk_manager@bsm.demo',
            now(), now()
        ),
        (
            'a2000000-0000-0000-0000-000000000003',
            'IRRBB_PARALLEL_UP', 'IRRBB Parallel Shift Up +200bps',
            'Six standard BCBS IRRBB shocks — parallel shift up scenario.',
            'regulatory', 'moderate', true, 'BCBS IRRBB Standard (2016) §99', true, 'alm_team@bsm.demo',
            now(), now()
        ),
        (
            'a2000000-0000-0000-0000-000000000004',
            'LIQUIDITY_STRESS', 'Combined Market & Idiosyncratic Liquidity Stress',
            'Simultaneous outflow stress: retail run-off 3x, wholesale 75%, HQLA fire-sale haircut +15%.',
            'internal', 'extreme', false, NULL, true, 'treasury@bsm.demo',
            now(), now()
        ),
        (
            'a2000000-0000-0000-0000-000000000005',
            'REVERSE_STRESS', 'Reverse Stress — LCR Breach Point',
            'Find the minimum adverse scenario that causes LCR < 100%. Used for ICAAP.',
            'reverse_stress', 'extreme', false, NULL, true, 'risk_manager@bsm.demo',
            now(), now()
        )
    """))

    conn.execute(sa.text("""
        INSERT INTO scenario_parameter_sets
            (id, scenario_id, parameter_type, parameter_name, shock_type,
             shock_value, asset_class, jurisdiction, currency, time_horizon_days,
             created_at, updated_at)
        VALUES
        -- RBI Severe: interest rate shock
        (gen_random_uuid(), 'a2000000-0000-0000-0000-000000000002', 'interest_rate', 'parallel_shift_bps', 'absolute', 300, NULL, 'IN', 'INR', 30, now(), now()),
        -- RBI Severe: credit migration
        (gen_random_uuid(), 'a2000000-0000-0000-0000-000000000002', 'credit', 'migration_factor', 'relative', 0.20, 'corporate', 'IN', NULL, 30, now(), now()),
        -- RBI Severe: equity shock
        (gen_random_uuid(), 'a2000000-0000-0000-0000-000000000002', 'market', 'equity_decline_pct', 'relative', -0.40, 'equity', NULL, 'INR', 30, now(), now()),
        -- IRRBB: parallel up 200bps
        (gen_random_uuid(), 'a2000000-0000-0000-0000-000000000003', 'interest_rate', 'parallel_shift_bps', 'absolute', 200, NULL, 'IN', 'INR', 365, now(), now()),
        -- Liquidity stress: retail run-off multiplier
        (gen_random_uuid(), 'a2000000-0000-0000-0000-000000000004', 'liquidity', 'retail_runoff_multiplier', 'relative', 3.0, NULL, NULL, 'INR', 30, now(), now()),
        -- Liquidity stress: wholesale run-off
        (gen_random_uuid(), 'a2000000-0000-0000-0000-000000000004', 'liquidity', 'wholesale_runoff_rate', 'absolute', 0.75, NULL, NULL, 'INR', 30, now(), now()),
        -- Liquidity stress: HQLA haircut addon
        (gen_random_uuid(), 'a2000000-0000-0000-0000-000000000004', 'liquidity', 'hqla_haircut_addon', 'absolute', 0.15, NULL, NULL, 'INR', 30, now(), now())
    """))

    # ------------------------------------------------------------------
    # 11. Balance sheet summary (demo computed values — not from Python engine)
    #     Note: in production this is always written by the capital engine.
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO balance_sheet_summaries
            (id, snapshot_id, entity_id, total_assets, total_liabilities,
             total_equity, total_off_balance_sheet, currency,
             compute_run_id, created_at, updated_at)
        VALUES (
            gen_random_uuid(),
            'd1000000-0000-0000-0000-000000000001',
            'a1000000-0000-0000-0000-000000000001',
            325000,   -- total assets (INR crores)
            292500,   -- total liabilities
            32500,    -- total equity (CET1 + AT1 + T2)
            18000,    -- off-balance-sheet commitments
            'INR',
            'e1000000-0000-0000-0000-000000000001',
            now(), now()
        )
    """))

    # ------------------------------------------------------------------
    # 12. Capital result (demo values)
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO capital_results
            (id, snapshot_id, entity_id, compute_run_id,
             cet1_capital, additional_tier1, tier2_capital, total_capital,
             rwa_credit, rwa_market, rwa_operational, total_rwa,
             cet1_ratio, tier1_ratio, total_capital_ratio, leverage_ratio,
             cet1_minimum, tier1_minimum, total_minimum, passes_all, currency,
             created_at, updated_at)
        VALUES (
            gen_random_uuid(),
            'd1000000-0000-0000-0000-000000000001',
            'a1000000-0000-0000-0000-000000000001',
            'e1000000-0000-0000-0000-000000000001',
            -- Capital stack (INR crores)
            22750, 3250, 6500, 32500,
            -- RWA
            175000, 12500, 15000, 202500,
            -- Ratios (22750/202500 = 11.23%)
            0.1123, 0.1283, 0.1605, 0.0832,
            -- Thresholds
            0.0450, 0.0600, 0.0800,
            true, 'INR',
            now(), now()
        )
    """))

    # ------------------------------------------------------------------
    # 13. LCR result (demo — 30-day net cash outflow computation)
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO lcr_results
            (id, snapshot_id, entity_id, compute_run_id,
             hqla_total, net_cash_outflows, total_outflows, total_inflows,
             inflow_cap_applied, lcr_ratio, minimum_ratio, passes, currency,
             created_at, updated_at)
        VALUES (
            'a3000000-0000-0000-0000-000000000001',
            'd1000000-0000-0000-0000-000000000001',
            'a1000000-0000-0000-0000-000000000001',
            'e1000000-0000-0000-0000-000000000001',
            -- HQLA: G-Secs at level 1 (no haircut) = 130400 crores
            130400,
            -- Net outflows = 30-day gross outflows - min(inflows, 75% of outflows)
            82600, 110000, 27400,
            true,
            -- LCR = 130400 / 82600 = 157.87%
            1.5787, 1.0, true, 'INR',
            now(), now()
        )
    """))

    conn.execute(sa.text("""
        INSERT INTO lcr_hqla_components
            (id, lcr_result_id, hqla_level, asset_class, gross_amount, haircut_rate, net_amount, cap_applies, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'level_1',  'sovereign', 130400, 0.00, 130400, false, now(), now()),
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'level_2a', 'corporate', 8160,   0.15, 6936,   false, now(), now())
    """))

    conn.execute(sa.text("""
        INSERT INTO lcr_outflow_components
            (id, lcr_result_id, outflow_category, deposit_type, customer_segment, gross_outflow, run_off_rate, net_outflow, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'retail_stable_deposits',     'retail_stable',            'retail',              80000, 0.03, 2400,  now(), now()),
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'retail_less_stable_deposits','retail_less_stable',        'retail',              45000, 0.10, 4500,  now(), now()),
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'operational_deposits_corp',  'operational_deposit',       'corporate',            8000, 0.25, 2000,  now(), now()),
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'non_op_deposits_corp',       'non_operational_deposit_non_financial','corporate',12000, 0.40, 4800,  now(), now()),
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'non_op_deposits_fi',         'non_operational_deposit_financial','financial_institution',4000,0.40,1600, now(), now()),
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'secured_wholesale_funding',  'secured_funding',           'financial_institution',10000,0.25, 2500,  now(), now()),
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'call_money_borrowed',        'non_operational_deposit_financial','financial_institution',3000,1.00,3000, now(), now())
    """))

    conn.execute(sa.text("""
        INSERT INTO lcr_inflow_components
            (id, lcr_result_id, inflow_category, asset_class, gross_inflow, inflow_rate, net_inflow, inflow_cap_applies, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'interbank_loans_maturing',   'bank',     8000,  1.0, 8000, false, now(), now()),
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'tbills_maturing',             'sovereign',19850, 1.0,19850, true,  now(), now()),
        (gen_random_uuid(), 'a3000000-0000-0000-0000-000000000001', 'repo_maturing',               'sovereign',10000, 1.0, 10000,false, now(), now())
    """))

    # ------------------------------------------------------------------
    # 14. NSFR result (demo)
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO nsfr_results
            (id, snapshot_id, entity_id, compute_run_id,
             available_stable_funding, required_stable_funding,
             nsfr_ratio, minimum_ratio, passes, currency,
             created_at, updated_at)
        VALUES (
            'a4000000-0000-0000-0000-000000000001',
            'd1000000-0000-0000-0000-000000000001',
            'a1000000-0000-0000-0000-000000000001',
            'e1000000-0000-0000-0000-000000000001',
            -- ASF: retail deposits + long-term corporate + equity
            252000,
            -- RSF: lending portfolio weighted by RSF factors
            198000,
            -- NSFR = 252000/198000 = 127.27%
            1.2727, 1.0, true, 'INR',
            now(), now()
        )
    """))

    conn.execute(sa.text("""
        INSERT INTO nsfr_asf_components
            (id, nsfr_result_id, funding_category, remaining_maturity_bucket, gross_amount, asf_factor, weighted_amount, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'tier1_capital',                 'gt_1y',   22750, 1.00, 22750, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'retail_deposits_stable_gt1y',   'gt_1y',   80000, 0.95, 76000, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'retail_deposits_stable_lt1y',   'lt_6m',   45000, 0.90, 40500, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'retail_term_deposits_gt1y',     'gt_1y',   45000, 0.95, 42750, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'retail_term_deposits_lt1y',     '6m_1y',   15000, 0.90, 13500, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'corporate_op_deposits',         'lt_6m',    8000, 0.50,  4000, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'corporate_non_op_deposits',     'lt_6m',   12000, 0.50,  6000, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'fi_deposits',                   'lt_6m',    4000, 0.00,     0, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'repo_short_term',               'lt_6m',   10000, 0.00,     0, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'call_money',                    'lt_6m',    3000, 0.00,     0, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'tier2_capital_gt1y',            'gt_1y',    6500, 1.00,  6500, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'retained_earnings',             'gt_1y',   40000, 1.00, 40000, now(), now())
    """))

    conn.execute(sa.text("""
        INSERT INTO nsfr_rsf_components
            (id, nsfr_result_id, asset_category, remaining_maturity_bucket, gross_amount, rsf_factor, weighted_amount, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'hqla_level1_unencumbered',      'any',   130400, 0.05,  6520, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'hqla_level2a',                  'any',     8160, 0.15,  1224, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'loans_retail_hl_lt1y',          'lt_6m',   2000, 0.50,  1000, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'loans_retail_hl_gt1y',          'gt_1y',  40000, 0.65, 26000, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'loans_corporate_lt1y',          'lt_6m',   8000, 0.50,  4000, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'loans_corporate_gt1y',          'gt_1y',  53750, 0.85, 45688, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'loans_sme',                     'gt_1y',    700, 0.85,   595, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'loans_interbank_lt6m',          'lt_6m',   8000, 0.15,  1200, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'corporate_bonds_gt1y',          'gt_1y',   8160, 0.50,  4080, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'cre_loans',                     'gt_1y',   1450, 1.00,  1450, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'defaulted_exposures',           'any',      240, 1.00,   240, now(), now()),
        (gen_random_uuid(), 'a4000000-0000-0000-0000-000000000001', 'other_assets',                  'any',   106003, 1.00,106003, now(), now())
    """))

    # ------------------------------------------------------------------
    # 15. Structural Liquidity (SLS) buckets — RBI DSB-II time bands
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO structural_liquidity_buckets
            (id, snapshot_id, entity_id, compute_run_id,
             time_bucket, bucket_order,
             total_inflows, total_outflows, net_position, cumulative_net,
             currency, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'd1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', '0_1d',   1,  15000, 13000,   2000,   2000, 'INR', now(), now()),
        (gen_random_uuid(), 'd1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', '1_7d',   2,   8000, 10000,  -2000,      0, 'INR', now(), now()),
        (gen_random_uuid(), 'd1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', '7_14d',  3,   5000,  4500,    500,    500, 'INR', now(), now()),
        (gen_random_uuid(), 'd1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', '14_28d', 4,  22000, 18000,   4000,   4500, 'INR', now(), now()),
        (gen_random_uuid(), 'd1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', '28d_3m', 5,  35000, 30000,   5000,   9500, 'INR', now(), now()),
        (gen_random_uuid(), 'd1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', '3m_6m',  6,  28000, 20000,   8000,  17500, 'INR', now(), now()),
        (gen_random_uuid(), 'd1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', '6m_1y',  7,  45000, 35000,  10000,  27500, 'INR', now(), now()),
        (gen_random_uuid(), 'd1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', '1y_3y',  8,  65000, 42000,  23000,  50500, 'INR', now(), now()),
        (gen_random_uuid(), 'd1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', '3y_5y',  9,  30000, 18000,  12000,  62500, 'INR', now(), now()),
        (gen_random_uuid(), 'd1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', 'e1000000-0000-0000-0000-000000000001', 'gt_5y',  10, 72000, 25000,  47000, 109500, 'INR', now(), now())
    """))

    # ------------------------------------------------------------------
    # 16. Regulatory filing metadata (Q4 FY2026 RBI DSB)
    # ------------------------------------------------------------------
    conn.execute(sa.text("""
        INSERT INTO regulatory_filings
            (id, snapshot_id, entity_id, return_type, filing_date,
             period_start, period_end, status, created_at, updated_at)
        VALUES
        (
            gen_random_uuid(),
            'd1000000-0000-0000-0000-000000000001',
            'a1000000-0000-0000-0000-000000000001',
            'RBI_DSB_I',
            '2026-04-21',
            '2026-03-01', '2026-03-31',
            'draft',
            now(), now()
        ),
        (
            gen_random_uuid(),
            'd1000000-0000-0000-0000-000000000001',
            'a1000000-0000-0000-0000-000000000001',
            'RBI_DSB_II',
            '2026-04-21',
            '2026-03-01', '2026-03-31',
            'draft',
            now(), now()
        )
    """))


def downgrade() -> None:
    conn = op.get_bind()
    # Remove demo data in dependency order
    conn.execute(sa.text("DELETE FROM regulatory_filings WHERE snapshot_id = 'd1000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM structural_liquidity_buckets WHERE snapshot_id = 'd1000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM nsfr_rsf_components WHERE nsfr_result_id = 'a4000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM nsfr_asf_components WHERE nsfr_result_id = 'a4000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM nsfr_results WHERE id = 'a4000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM lcr_inflow_components WHERE lcr_result_id = 'a3000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM lcr_outflow_components WHERE lcr_result_id = 'a3000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM lcr_hqla_components WHERE lcr_result_id = 'a3000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM lcr_results WHERE id = 'a3000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM capital_results WHERE snapshot_id = 'd1000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM balance_sheet_summaries WHERE snapshot_id = 'd1000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM scenario_parameter_sets WHERE scenario_id IN ('a2000000-0000-0000-0000-000000000001','a2000000-0000-0000-0000-000000000002','a2000000-0000-0000-0000-000000000003','a2000000-0000-0000-0000-000000000004','a2000000-0000-0000-0000-000000000005')"))
    conn.execute(sa.text("DELETE FROM scenarios WHERE code IN ('BASE_CASE','RBI_SEVERE','IRRBB_PARALLEL_UP','LIQUIDITY_STRESS','REVERSE_STRESS')"))
    conn.execute(sa.text("DELETE FROM collateral WHERE position_id LIKE 'f1000000%'"))
    conn.execute(sa.text("DELETE FROM positions WHERE id LIKE 'f1000000%'"))
    conn.execute(sa.text("DELETE FROM compute_runs WHERE id = 'e1000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM snapshots WHERE id = 'd1000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM counterparties WHERE id LIKE 'c1000000%'"))
    conn.execute(sa.text("DELETE FROM products WHERE id LIKE 'b2000000%'"))
    conn.execute(sa.text("DELETE FROM product_groups WHERE id LIKE 'b1000000%'"))
    conn.execute(sa.text("DELETE FROM entity_capital_requirements WHERE entity_id = 'a1000000-0000-0000-0000-000000000001'"))
    conn.execute(sa.text("DELETE FROM legal_entities WHERE code IN ('BSMDB','BSMSG')"))
    conn.execute(sa.text("DELETE FROM reference_ccf"))
    conn.execute(sa.text("DELETE FROM reference_run_off_rates"))
    conn.execute(sa.text("DELETE FROM reference_hqla_haircuts"))
    conn.execute(sa.text("DELETE FROM reference_risk_weights"))
    conn.execute(sa.text("DELETE FROM reference_yield_curves WHERE as_of_date = '2026-03-31'"))
