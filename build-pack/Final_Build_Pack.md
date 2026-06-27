# Final Build Pack
## AI-Powered Balance Sheet Management & Regulatory Reporting Platform

**Version:** 1.0 (Release Candidate)
**Status:** Production-Ready Build Specification
**Owner:** Platform Engineering
**Last Updated:** 2026-06-28

---

## 1. Executive Summary

This platform is a regtech + ALM (Asset-Liability Management) system for banks, NBFCs, and large corporate treasuries. It combines two distinct computational layers that **must not be confused**:

| Layer | Role | Implementation |
|---|---|---|
| **Reasoning Layer** | Interprets regulation, explains variance, drafts disclosures, narrates anomalies, handles conversational analytics | Claude (LLM via Anthropic API) |
| **Compute Layer** | Performs all numerical work: RWA, LCR, NSFR, capital ratios, ECL, ALM gaps, stress tests, sensitivities | Python (deterministic, versioned, audit-logged) |

**Core principle:** the LLM never computes regulatory numbers. Python computes them, the LLM explains and reasons about them. Every number shown to a user or filed with a regulator is traceable to a deterministic Python function with a version hash.

The platform delivers:

- Automated regulatory return preparation (Basel III, IFRS 9, RBI DSB, FR Y-9C / FFIEC, COREP/FINREP)
- Real-time balance sheet position, capital adequacy, liquidity ratios
- ALM workbench: gap analysis, EVE, NII sensitivity, FTP
- Stress testing (regulatory and internal scenarios)
- AI-generated variance commentary, exception narratives, disclosure drafts
- Conversational analytics ("explain why LCR fell 8% this week")
- Full audit trail with reproducible calculations

---

## 2. Architectural Overview

### 2.1 The Two-Layer Contract

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│  (Dashboards, Reports, Conversational UI, Workpapers)       │
└────────────────────────┬────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
      ┌───────▼────────┐   ┌────────▼─────────┐
      │   REASONING    │   │     COMPUTE      │
      │     LAYER      │◄──┤      LAYER       │
      │   (Claude)     │   │    (Python)      │
      │                │   │                  │
      │ • Explain      │   │ • Calculate RWA  │
      │ • Narrate      │   │ • LCR / NSFR     │
      │ • Draft        │   │ • ECL (IFRS 9)   │
      │ • Reason       │   │ • Capital ratios │
      │ • Q&A          │   │ • ALM gaps       │
      │ • Plan         │   │ • Stress tests   │
      └────────┬───────┘   └────────┬─────────┘
               │                    │
               └──────────┬─────────┘
                          │
                ┌─────────▼──────────┐
                │   DATA PLATFORM    │
                │  • Position store  │
                │  • Reference data  │
                │  • Audit log       │
                │  • Snapshots       │
                └────────────────────┘
```

### 2.2 What Claude Does (and Doesn't Do)

**Claude does:**
- Interpret a regulatory paragraph and map it to a calculation function
- Generate the natural-language narrative around a number Python produced
- Summarise a 200-page IFRS 9 staging policy into operational rules
- Draft Pillar 3 disclosures from structured inputs
- Answer "why did our CET1 ratio drop 30bps?" by reading Python's variance decomposition
- Suggest which scenarios to run for a given portfolio stress
- Triage and explain reconciliation breaks
- Compose regulator-facing cover letters

**Claude does NOT:**
- Compute any regulatory ratio
- Apply any risk weight
- Perform any sum, average, weighted average, or ratio
- Determine any threshold breach
- Generate any filed number
- Modify any audit-logged value

If a user asks Claude "what is our LCR?", Claude calls the Python `compute_lcr()` endpoint and reports the returned value verbatim. It never estimates.

### 2.3 Determinism and Reproducibility

Every Python calculation function:

1. Is pure (same inputs → same outputs, no hidden state)
2. Is versioned (semantic version + git hash recorded with every output)
3. Logs inputs, outputs, version, and timestamp to the audit store
4. Has at least one golden test against a regulator-published example
5. Has property-based tests for invariants (e.g., LCR numerator components sum correctly)

Snapshot policy: every reportable number is computed from a frozen snapshot of the position and reference data. Snapshots are immutable. Recomputation against the same snapshot must produce bit-identical results.

---

## 3. Module Breakdown

### 3.1 Data Foundation (`/data`)

- **Position Store:** loans, deposits, securities, derivatives, off-balance-sheet exposures
- **Reference Data:** ratings, curves, FX rates, regulatory parameters (risk weights, haircuts, CCFs)
- **Counterparty Master:** legal entity, sector, geography, group structure
- **Product Catalog:** instrument type, regulatory classification, behavioural assumptions
- **Snapshot Engine:** point-in-time freeze for reporting dates

### 3.2 Compute Engines (`/engines`)

| Engine | Purpose | Key Functions |
|---|---|---|
| `rwa_engine` | Risk-weighted assets | Credit SA, Credit IRB-F, Market SA, Op Risk SA |
| `liquidity_engine` | Basel III liquidity | LCR, NSFR, HQLA classification, run-off rates |
| `capital_engine` | Capital adequacy | CET1, AT1, T2, leverage ratio, buffer requirements |
| `ecl_engine` | IFRS 9 impairment | Staging, 12M ECL, Lifetime ECL, SICR triggers |
| `alm_engine` | Asset-liability management | Repricing gap, EVE, NII sensitivity, behavioural overlays |
| `ftp_engine` | Funds transfer pricing | Matched-maturity FTP, liquidity premium, option cost |
| `stress_engine` | Scenario analysis | Regulatory scenarios, reverse stress, sensitivity grids |
| `irrbb_engine` | Interest rate risk in banking book | EVE, NII under 6 standard shocks |

Each engine exposes a versioned function API and an HTTP/RPC endpoint.

### 3.3 Reasoning Modules (`/reasoning`)

- **Variance Narrator:** consumes structured deltas from compute engines, produces commentary
- **Exception Triage:** classifies and explains data quality and reconciliation breaks
- **Disclosure Drafter:** generates Pillar 3, IFRS 9, and IFRS 17 narrative disclosures
- **Conversational Q&A:** natural language interface over structured outputs
- **Policy Interpreter:** maps regulatory text to operational rules (advisory only, always reviewed)
- **Scenario Designer:** suggests stress scenarios given a portfolio profile

Every reasoning module operates on **outputs from the compute layer**, never on raw positions to estimate ratios.

### 3.4 Reporting Layer (`/reports`)

- **Regulatory Returns:** templated outputs for filed returns (RBI DSB, FFIEC, COREP, FINREP)
- **Management Packs:** ALCO pack, Board risk dashboard, CRO daily
- **Workpapers:** audit-grade calculation trails with formula transparency
- **Disclosures:** Pillar 3 quantitative tables and qualitative narrative

### 3.5 Workflow Layer (`/workflow`)

- **Close Calendar:** month-end / quarter-end task orchestration
- **Maker-Checker:** four-eyes approval on every filed number
- **Sign-Off:** electronic attestation with role binding
- **Distribution:** secure delivery to regulators and internal stakeholders

### 3.6 Observability (`/observability`)

- **Audit Log:** every compute call, every reasoning generation, every user action
- **Lineage Graph:** trace any filed number back to source positions
- **Quality Metrics:** data quality scores, exception counts, late data alerts
- **Performance:** latency, throughput, error rates per engine

---

## 4. Data Model (Domain Entities)

```
Counterparty
  ├── id, name, lei, sector, geography, group_id, rating
  └── exposures → Position[]

Position
  ├── id, counterparty_id, product_code, currency, notional
  ├── booked_amount, fair_value, accrued_interest
  ├── maturity_date, repricing_date, behavioural_maturity
  ├── credit_grade, ifrs9_stage, days_past_due
  └── collateral → Collateral[]

ReferenceData
  ├── risk_weights (by asset class, rating, jurisdiction)
  ├── haircuts (by HQLA level, by collateral type)
  ├── run_off_rates (by deposit type, customer segment)
  ├── ccf (credit conversion factors by commitment type)
  └── curves (zero curves, basis curves, FX, vol)

Snapshot
  ├── id, reporting_date, frozen_at, frozen_by
  ├── position_hash, reference_hash
  └── status: draft | locked | filed

ComputeRun
  ├── id, snapshot_id, engine, function, version
  ├── inputs_hash, outputs_hash, started_at, duration_ms
  └── outputs → numeric results + diagnostics

ReasoningRun
  ├── id, compute_run_ids[], prompt_hash, model_version
  ├── outputs (text), tokens_in, tokens_out
  └── reviewer_id, reviewed_at, accepted | edited | rejected
```

---

## 5. Tech Stack

| Concern | Choice | Rationale |
|---|---|---|
| Compute language | Python 3.12 | Numerical libraries, regulatory community standard |
| Numerical | NumPy, pandas, scipy | Battle-tested |
| Validation | Pydantic v2 | Type safety at data boundaries |
| Workflow | Prefect / Airflow | Auditable orchestration |
| API | FastAPI | Typed, async, auto-documented |
| Persistence | PostgreSQL + S3 (for snapshots) | ACID for transactional, object store for immutable snapshots |
| Reasoning | Anthropic Claude API | Per architecture |
| Frontend | React + TypeScript | Standard |
| Charts | Recharts + D3 (for specialised viz) | Standard |
| Auth | OIDC (Okta / Azure AD) | Enterprise standard |
| Audit log | Append-only, hash-chained | Tamper-evidence |
| Observability | OpenTelemetry → Datadog / Grafana | Standard |
| Secrets | HashiCorp Vault / AWS Secrets Manager | Standard |

---

## 6. Phase Index

Build phases 1–27. Each phase has its own deliverable, acceptance criteria, and exit gate.

| # | Phase | Focus |
|---|---|---|
| 1 | Bootstrap | Repo, CI, base infra |
| 2 | Data Foundation | Position, counterparty, reference data |
| 3 | Snapshot Engine | Point-in-time freeze |
| 4 | RWA — Credit SA | Standardised credit risk |
| 5 | RWA — Credit IRB | IRB foundation approach |
| 6 | RWA — Market | Market risk SA |
| 7 | RWA — Operational | BIA / SA-OR |
| 8 | Capital Engine | CET1/T1/Total Capital, buffers |
| 9 | LCR | HQLA, net cash outflows, LCR computation |
| 10 | NSFR | ASF, RSF, NSFR computation |
| 11 | Leverage Ratio | Tier 1 / exposure measure |
| 12 | IFRS 9 — Staging | SICR rules, stage classification |
| 13 | IFRS 9 — ECL | PD, LGD, EAD, 12M & Lifetime ECL |
| 14 | ALM — Repricing Gap | Time bucket gap |
| 15 | ALM — EVE | Economic value of equity, six shocks |
| 16 | ALM — NII Sensitivity | Earnings-at-risk |
| 17 | FTP | Matched-maturity, liquidity premium |
| 18 | Stress Testing | Regulatory + internal scenarios |
| 19 | Reasoning — Variance | Variance commentary generator |
| 20 | Reasoning — Disclosures | Pillar 3, IFRS 9 narrative |
| 21 | Reasoning — Conversational | Natural language Q&A over outputs |
| 22 | Reporting — Returns | RBI DSB, FFIEC, COREP, FINREP templates |
| 23 | Workflow — Close | Calendar, dependencies, status |
| 24 | Workflow — Sign-off | Maker-checker, attestation |
| 25 | Observability | Audit log, lineage graph, metrics |
| 26 | Hardening | Security, performance, DR |
| 27 | Productionisation | See `Phase27.md` |

Detailed Phase 27 specification: see `Phase27.md`.

---

## 7. Quality Gates

A phase exits only when **all** of the following pass:

1. **Golden tests:** at least one regulator-published example reproduced to the cent.
2. **Property tests:** all invariants hold over 1000+ generated cases.
3. **Determinism test:** same snapshot run twice produces identical hash.
4. **Audit completeness:** every output is traceable to inputs through audit log.
5. **Performance budget:** engine runs within the SLA in section 11.
6. **Documentation:** function-level docstring, regulator citation, formula in LaTeX, worked example.
7. **Reasoning boundary:** no LLM call substitutes for a deterministic calculation.

---

## 8. Reasoning Layer Discipline

### 8.1 Prompt Hygiene

All prompts to Claude include:

- A frozen JSON of structured inputs from compute layer
- The reporting date and snapshot ID
- Explicit instruction: "Do not produce numerical values not present in the provided inputs"
- A schema for the expected output (where structured)

### 8.2 Output Discipline

Every reasoning output is:

- Tagged with the compute runs it depends on
- Reviewed by an authorised user before publication (for filed disclosures)
- Reversible — the platform stores the prompt, the model version, and the output for replay

### 8.3 Forbidden Patterns

- Asking Claude to "estimate the LCR" — always compute it
- Asking Claude to "calculate the weighted average" — Python does this
- Allowing Claude's text to overwrite a compute output
- Filing a regulatory number that originated from an LLM response

### 8.4 Permitted Patterns

- "Explain the drivers behind this 30bps CET1 movement, given the variance decomposition below"
- "Draft the Pillar 3 narrative for credit risk based on the following structured table"
- "Classify this reconciliation break and suggest the next investigative step"
- "Translate this RBI circular into a list of operational rule changes"

---

## 9. Security & Compliance

### 9.1 Access Control

- RBAC with roles: Viewer, Preparer, Reviewer, Approver, Admin
- Segregation of duties enforced: preparer ≠ reviewer ≠ approver
- All actions logged with user, timestamp, IP, session

### 9.2 Data Protection

- TLS 1.3 in transit
- AES-256 at rest
- PII minimisation: customer-level data accessed only where required
- Tokenisation for cross-environment movement

### 9.3 Regulatory Considerations

- Model risk: every model registered in model inventory, periodically validated
- LLM use: documented as advisory layer, never determinative for filed numbers
- Audit trail: 7-year retention (or jurisdiction-specific)
- Reproducibility: any historical filing must be reproducible from snapshot + code version

### 9.4 LLM-Specific Controls

- Prompts and completions logged
- No customer PII in prompts (use tokenised references)
- Output review required before any external use
- Model version pinned per release; upgrades tested against golden disclosure set

---

## 10. Performance SLAs

| Operation | Target | Hard Limit |
|---|---|---|
| Daily LCR computation (full bank) | 5 min | 15 min |
| Monthly capital adequacy run | 30 min | 90 min |
| Single ECL recompute (one portfolio) | 60s | 5 min |
| Variance narrative generation | 10s | 60s |
| Conversational Q&A response | 3s | 15s |
| Snapshot freeze | 2 min | 10 min |
| Regulatory return export | 5 min | 30 min |

---

## 11. Repository Layout

See `Repository_Reconciliation.md` for the consolidated repository structure and migration from prior multi-repo layout.

Target layout (post-reconciliation):

```
platform/
├── apps/
│   ├── api/              # FastAPI service
│   ├── web/              # React frontend
│   └── workers/          # Async job workers
├── engines/
│   ├── rwa/
│   ├── liquidity/
│   ├── capital/
│   ├── ecl/
│   ├── alm/
│   ├── ftp/
│   ├── stress/
│   └── irrbb/
├── reasoning/
│   ├── variance/
│   ├── disclosures/
│   ├── conversational/
│   └── triage/
├── data/
│   ├── ingest/
│   ├── snapshot/
│   └── reference/
├── reports/
│   ├── regulatory/
│   ├── management/
│   └── workpapers/
├── workflow/
├── observability/
├── shared/
│   ├── domain/           # Pydantic models
│   ├── audit/
│   └── testing/
├── tests/
│   ├── golden/           # Regulator-published examples
│   ├── property/
│   └── e2e/
└── docs/
```

---

## 12. Build & Release

- Trunk-based development on `main`
- Feature flags for incremental release of engines
- Semantic versioning per engine
- Calendar versioning for the platform release (`2026.06.0`)
- Release notes auto-generated, then narrated by Claude for the human-readable changelog
- Every release reproduces a golden set of historical filings byte-for-byte

---

## 13. Roles & Responsibilities

| Role | Owns |
|---|---|
| Platform Lead | Architecture, phase gates |
| Engine Owners | One per engine; calculation correctness, golden tests |
| Reasoning Lead | Prompt design, output review process, model selection |
| Reg Tech SME | Regulatory citations, rule interpretation |
| Data Platform | Position store, snapshots, lineage |
| SRE | Observability, performance, DR |
| Security | Access, PII, audit |
| QA | Golden test maintenance, regression, property tests |

---

## 14. Open Questions / Out of Scope (v1)

- IFRS 17 (insurance) — deferred to v2
- IRB-A (advanced) — deferred to v2; v1 supports SA and IRB-F only
- FRTB (fundamental review of trading book) — v2
- Solo + Consolidated reporting — v1 supports both; intercompany elimination in v1.1
- Real-time intraday LCR — v2; v1 is daily

---

## 15. Glossary

- **ALM** — Asset-Liability Management
- **CET1** — Common Equity Tier 1 capital
- **ECL** — Expected Credit Loss (IFRS 9)
- **EVE** — Economic Value of Equity
- **FTP** — Funds Transfer Pricing
- **HQLA** — High-Quality Liquid Assets
- **IRRBB** — Interest Rate Risk in the Banking Book
- **LCR** — Liquidity Coverage Ratio
- **NSFR** — Net Stable Funding Ratio
- **PD/LGD/EAD** — Probability of Default / Loss Given Default / Exposure at Default
- **RWA** — Risk-Weighted Assets
- **SICR** — Significant Increase in Credit Risk
- **SA / IRB** — Standardised Approach / Internal Ratings-Based

---

## 16. Companion Documents

- `Repository_Reconciliation.md` — Repo consolidation plan
- `Phase27.md` — Final productionisation phase
- `Demo_Mode.md` — Sandbox / demo configuration
- `UI_Polish.md` — Frontend finishing items
- `Deployment_Checklist.md` — Pre-go-live gate

---

*End of Final Build Pack.*
