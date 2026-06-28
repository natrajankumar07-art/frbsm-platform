# Engine Validation Report — Epic 2C
**Date:** 2026-06-28  
**Snapshot:** d1000000-0000-0000-0000-000000000001 (BSM Demo Bank, 2026-03-31)  
**Test run:** `uv run pytest tests/unit/engines/ -v` — **126/126 passed**

---

## 1. Engine Inventory

| Engine | Module | VERSION | Formula Refs |
|--------|--------|---------|--------------|
| LCR | `engines/liquidity/lcr.py` | 1.0.0 | BCBS LCR30.40, LCR30.42, LCR30.43, LCR40.73 |
| NSFR | `engines/liquidity/nsfr.py` | 1.0.0 | BCBS NSF10, NSF20, NSF30 |
| SLS | `engines/liquidity/sls.py` | 1.0.0 | RBI DSB-II, RBI Master Direction 2019 |
| Capital | `engines/capital/engine.py` | 1.0.0 | BCBS CRE20, CAP10, LEV10, RBI 2023 |
| Balance Sheet | `engines/balance_sheet/engine.py` | 1.0.0 | IFRS Conceptual Framework, RBI Format A |
| Cashflow | `engines/alm/cashflow.py` | 1.0.0 | RBI DSB-II, ALM standard |
| Liquidity Gap | `engines/alm/gap.py` | 1.0.0 | ALM maturity gap, RBI DSB-II |
| Scenario | `engines/stress/scenario.py` | 1.0.0 | Absolute / relative / replace shocks |
| Stress Test | `engines/stress/engine.py` | 1.0.0 | BCBS Stress principles 2018, RBI framework |

---

## 2. Calculation Dependency Diagram

```
Inputs (positions, cashflows, capital data)
        │
        ├──► BalanceSheetInput ──► compute_balance_sheet ──► BalanceSheetResult
        │                                                           (total_assets)
        │                                                                │
        ├──► CashflowInput ──────► compute_cashflow_buckets ──► CashflowResult
        │                                                                │
        │                         (total_assets)──────────────► compute_liquidity_gap ──► LiquidityGapResult
        │
        ├──► CashflowInput ──────► compute_sls ──────────────► SLSResult
        │
        ├──► LCRInput ───────────► compute_lcr ──────────────► LCRResult
        │         ▲
        │         │ apply_lcr_shocks (scenario params)
        │
        ├──► NSFRInput ──────────► compute_nsfr ─────────────► NSFRResult
        │         ▲
        │         │ apply_nsfr_shocks (scenario params)
        │
        ├──► CapitalInput ───────► compute_capital ──────────► CapitalResult
        │         ▲
        │         │ apply_capital_shocks (scenario params)
        │
        └──► StressTestInput ────► compute_stress_test ──────► StressTestResult
                  │                       │
                  │               (orchestrates LCR, NSFR, Capital)
                  │               baseline ──► shocked ──► MetricDelta per metric
                  │
              ScenarioParameter[]
              (shock_type: absolute | relative | replace)

Shared infrastructure (all engines use):
  engines/common/utils.py     canonical_hash(), quantize(), safe_divide()
  engines/common/audit.py     EngineTrace, EngineResult[T], build_trace()
  engines/common/models.py    Input models for all engines
```

---

## 3. Golden Validation — BSM Demo Bank

### 3.1 LCR (from seeded component data)

| Item | Expected | Computed | Match |
|------|----------|----------|-------|
| HQLA Level 1 | 130,400 | 130,400 | ✓ |
| HQLA Level 2A net (15% haircut) | 6,936 | 6,936 | ✓ |
| L2 cap applied | No | No | ✓ |
| Total outflows | 20,800 | 20,800 | ✓ |
| Eligible inflows (capped at 75% of 20,800 = 15,600) | 15,600 | 15,600 | ✓ |
| Inflow cap applied | Yes | Yes | ✓ |
| NCO | 5,200 | 5,200 | ✓ |
| LCR ratio | >1.5 | 26.41 | ✓ |
| Passes | Yes | Yes | ✓ |

> **Note on seeded data inconsistency:** The top-level `lcr_results` record has `total_outflows=110,000` which does not match the component sum of 20,800. Tests use component-level data (self-consistent). The 110,000 figure appears to be a seed data error.

### 3.2 NSFR (from seeded component data)

| Item | Expected | Computed | Match |
|------|----------|----------|-------|
| ASF | 252,000 | 252,000 | ✓ |
| RSF | ~198,000 | 197,999.50 | ✓ (DB rounded 53,750×0.85=45,687.50 → 45,688) |
| NSFR ratio | 252,000/197,999.50 = 1.2727 | 1.2727 | ✓ |
| Passes | Yes | Yes | ✓ |

> **Note on RSF rounding:** The seeded `nsfr_results.required_stable_funding=198,000` is the DB-rounded value. The engine correctly computes 197,999.50 (exact Decimal multiplication). The difference of 0.50 is from the `loans_corporate_gt1y` position (53,750 × 0.85 = 45,687.50, stored as 45,688 in DB).

### 3.3 Capital (from seeded capital data)

| Metric | Expected | Computed | Match |
|--------|----------|----------|-------|
| CET1 | 22,750 | 22,750 | ✓ |
| AT1 | 3,250 | 3,250 | ✓ |
| T2 | 6,500 | 6,500 | ✓ |
| T1 | 26,000 | 26,000 | ✓ |
| Total Capital | 32,500 | 32,500 | ✓ |
| Credit RWA | 202,500 | 202,500 | ✓ |
| CET1 ratio | 0.1123 | 0.1123 | ✓ |
| T1 ratio | 0.1283 | 0.1283 | ✓ |
| TCR | 0.1605 | 0.1605 | ✓ |
| Leverage | 0.0832 | 0.0832 | ✓ |
| All minimums | Pass | Pass | ✓ |

### 3.4 Balance Sheet

| Metric | Expected | Computed | Match |
|--------|----------|----------|-------|
| Total assets | 325,000 | 325,000 | ✓ (verified via simple_golden test) |
| Total liabilities | 292,500 | 292,500 | ✓ |
| Equity | 32,500 | 32,500 | ✓ |
| Balances | True | True | ✓ |

---

## 4. Test Coverage Summary

| Test File | Tests | Passed | Classes Covered |
|-----------|-------|--------|-----------------|
| test_lcr.py | 22 | 22 | Basic formula, inflow cap, HQLA caps, determinism, golden |
| test_nsfr.py | 10 | 10 | Basic formula, ASF/RSF factors, determinism, golden |
| test_capital.py | 15 | 15 | Ratios, RWA, leverage, pass/fail, determinism, golden |
| test_balance_sheet.py | 14 | 14 | Classification, equity, balances flag, breakdown, golden |
| test_cashflow.py | 22 | 22 | All 10 bucket boundaries, sign convention, cumulative, gap |
| test_sls.py | 18 | 18 | Bucket definitions, boundaries, net/cumulative, determinism |
| test_stress.py | 25 | 25 | All 3 shock types, all shock targets, full engine, golden |
| **TOTAL** | **126** | **126** | |

---

## 5. Engineering Properties Verified

| Property | Mechanism | Verified |
|----------|-----------|---------|
| **Decimal arithmetic** | All engines use `decimal.Decimal`; no `float` | ✓ |
| **Determinism** | `canonical_hash(SHA-256)` on serialised inputs and outputs | ✓ |
| **Pure functions** | No DB calls, no I/O in any engine; all inputs via typed models | ✓ |
| **Auditability** | `EngineTrace` (engine, version, function, inputs_hash, outputs_hash, computed_at, formula_refs) | ✓ |
| **Traceability** | Every formula referenced to BCBS/RBI source in `formula_refs` | ✓ |
| **Repeatability** | Same inputs → identical `inputs_hash` and `outputs_hash` across runs | ✓ |
| **Version tagging** | `VERSION = "1.0.0"` constant in every engine module | ✓ |
| **Independent engines** | No cross-engine imports except stress orchestrator | ✓ |

---

## 6. Stress Test Directional Verification

| Shock Applied | Expected Effect | Verified |
|--------------|-----------------|---------|
| `liquidity.outflow_shock` relative +50% | LCR ratio decreases | ✓ |
| `liquidity.hqla_shock` relative -30% | LCR ratio decreases | ✓ |
| `capital.rwa_shock` relative +30% | CET1 ratio decreases | ✓ |
| `liquidity.asf_shock` relative -10% | NSFR ratio decreases | ✓ |
| Outflow shock capped at 100% run-off | No run-off rate > 1.0 | ✓ |
| HQLA shock floored at 0 | No negative HQLA | ✓ |
| Non-matching parameter type ignored | No unintended side-effect | ✓ |

---

## 7. Known Data Issues

1. **LCR seeded summary inconsistency**: `lcr_results.total_outflows = 110,000` but component sum = 20,800. Likely a seed data entry error. Component data is self-consistent and used for golden tests.

2. **NSFR RSF rounding**: `nsfr_results.required_stable_funding = 198,000` (rounded). Exact engine output is 197,999.50. The ±0.50 difference stems from `loans_corporate_gt1y: 53,750 × 0.85 = 45,687.50` which the DB seed rounded to 45,688. Engine behaviour is correct.
