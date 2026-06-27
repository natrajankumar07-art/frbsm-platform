# Deployment Checklist

**Purpose:** The gate the platform must pass before going live. Every item below must be checked off, with named accountable owners, evidence linked, and date recorded. No item is optional. No item is deferrable.

**Status:** Pre-Production Gate
**Required by:** All workstreams in `Phase27.md`
**Sign-off requires:** Platform Lead, CRO, CFO, CISO, Head of Compliance

---

## How to Use This Checklist

- Each section is owned by a named role; that owner is accountable for evidence
- Evidence is a link to: a test report, an artefact in the audit store, a signed memo, or a recorded session
- Items marked **[Blocker]** must be green for go-live; **[Strong]** must be green or have a documented exception approved by all five sign-off roles
- Re-validation cadence noted where applicable

---

## Section A — Architectural Invariants

**Owner:** Platform Lead

| # | Item | Status | Evidence |
|---|---|---|---|
| A1 | **[Blocker]** Reasoning layer does not perform any numerical regulatory computation. Verified by import linter and code audit | | |
| A2 | **[Blocker]** No reasoning module imports `numpy`, `pandas`, `scipy`, or `engines/*` | | |
| A3 | **[Blocker]** No engine module calls the Anthropic API | | |
| A4 | **[Blocker]** Every filed number traces to a Python function, version-pinned, snapshot-pinned | | |
| A5 | **[Blocker]** Reasoning outputs cannot overwrite compute outputs in any data path | | |
| A6 | **[Strong]** Every prompt template registered in `reasoning/prompts/` with eval set | | |
| A7 | **[Strong]** Boundary lint rules in CI as a required check | | |

---

## Section B — Determinism & Reproducibility

**Owner:** Platform Lead + Reg Tech SME

| # | Item | Status | Evidence |
|---|---|---|---|
| B1 | **[Blocker]** Determinism CI green for 30 consecutive nights | | |
| B2 | **[Blocker]** Last 12 months of historical filings reproduced bit-identical from archived snapshots | | |
| B3 | **[Blocker]** Snapshot integrity verification job green for ≥30 days | | |
| B4 | **[Blocker]** Lineage tool can resolve any filed number to function + version + snapshot in <5s | | |
| B5 | **[Blocker]** Every engine has at least one golden test from a regulator-published example | | |
| B6 | **[Blocker]** Every engine has property tests with ≥1000 cases passing | | |
| B7 | **[Strong]** Property test coverage report shows no untested branches in core paths | | |

---

## Section C — Calculation Correctness (Per-Engine Sign-off)

**Owner:** Engine Owners + Reg Tech SME

For each engine below, all four sub-items required:

- a. Regulator-published example reproduced exactly
- b. SME walkthrough completed; formulas, citations, edge cases verified
- c. Property tests green
- d. Documentation complete (citation, formula, worked example)

| Engine | a | b | c | d | Owner |
|---|---|---|---|---|---|
| RWA — Credit SA | | | | | |
| RWA — Credit IRB-F | | | | | |
| RWA — Market SA | | | | | |
| RWA — Operational | | | | | |
| Capital (CET1/T1/Total, buffers, leverage) | | | | | |
| LCR | | | | | |
| NSFR | | | | | |
| ECL Staging (IFRS 9) | | | | | |
| ECL Computation (12M, Lifetime) | | | | | |
| ALM — Repricing Gap | | | | | |
| ALM — EVE | | | | | |
| ALM — NII Sensitivity | | | | | |
| FTP | | | | | |
| Stress Testing | | | | | |
| IRRBB | | | | | |

---

## Section D — Reasoning Layer Validation

**Owner:** Reasoning Lead

| # | Item | Status | Evidence |
|---|---|---|---|
| D1 | **[Blocker]** Eval suite for all production reasoning modules passes at ≥95% on golden set | | |
| D2 | **[Blocker]** Model version pinned in config; upgrade procedure documented | | |
| D3 | **[Blocker]** Prompt-injection defences tested with adversarial prompt suite | | |
| D4 | **[Blocker]** No PII reaches LLM prompts; tokenised references only — verified | | |
| D5 | **[Blocker]** Every external-bound reasoning output requires human sign-off in workflow | | |
| D6 | **[Blocker]** Reasoning output schemas validated; non-conforming outputs raise, not partial-render | | |
| D7 | **[Strong]** Cost & latency budgets set per module; alerting wired | | |
| D8 | **[Strong]** Disagreement protocol documented (compute always wins) | | |
| D9 | **[Strong]** Per-tenant LLM spend cap configured | | |

---

## Section E — Data Foundation

**Owner:** Data Platform

| # | Item | Status | Evidence |
|---|---|---|---|
| E1 | **[Blocker]** Position ingest pipelines green for ≥30 days, with all source systems reporting | | |
| E2 | **[Blocker]** Reference data freshness alerts wired; thresholds defined per dataset | | |
| E3 | **[Blocker]** Snapshot freeze procedure tested; freeze-to-unfreeze cycle verified | | |
| E4 | **[Blocker]** Counterparty master deduplication verified; LEI coverage measured and documented | | |
| E5 | **[Strong]** Data quality metrics dashboard live | | |
| E6 | **[Strong]** Late-data handling policy documented; affects which workflows are released | | |

---

## Section F — Performance & Capacity

**Owner:** SRE + Platform Lead

| # | Item | Status | Evidence |
|---|---|---|---|
| F1 | **[Blocker]** Load test at 1.5x expected peak met all SLAs in `Final_Build_Pack.md` §10 | | |
| F2 | **[Blocker]** 72-hour soak test passed with no memory leaks, no degradation | | |
| F3 | **[Blocker]** Production capacity provisioned with documented headroom | | |
| F4 | **[Strong]** Backpressure behaviour tested on conversational queue saturation | | |
| F5 | **[Strong]** Async batching for variance narratives benchmarked | | |
| F6 | **[Strong]** Flame graphs captured for top 5 slowest engines; documented hot paths | | |

---

## Section G — Disaster Recovery & Business Continuity

**Owner:** SRE

| # | Item | Status | Evidence |
|---|---|---|---|
| G1 | **[Blocker]** RTO and RPO targets met in most recent failover drill | | |
| G2 | **[Blocker]** Cross-region replication verified for PostgreSQL and S3 | | |
| G3 | **[Blocker]** Audit log durability verified via simulated failure | | |
| G4 | **[Blocker]** Backup restore-and-validate green for 4 consecutive weeks | | |
| G5 | **[Blocker]** Failover runbook published, rehearsed, and dated within last quarter | | |
| G6 | **[Strong]** Data corruption recovery procedure tested | | |

---

## Section H — Security

**Owner:** CISO + Security

| # | Item | Status | Evidence |
|---|---|---|---|
| H1 | **[Blocker]** Penetration test complete; zero open Critical, zero open High at go-live | | |
| H2 | **[Blocker]** Threat model documented (STRIDE + LLM-specific) and signed off | | |
| H3 | **[Blocker]** All secrets in vault; no secrets in code, config, or env vars (verified by scan) | | |
| H4 | **[Blocker]** Audit log tamper-evidence verified; hash chain unbroken for ≥30 days | | |
| H5 | **[Blocker]** TLS 1.3 enforced on all external endpoints | | |
| H6 | **[Blocker]** AES-256 at rest verified | | |
| H7 | **[Blocker]** RBAC roles in place; segregation of duties enforced (preparer ≠ reviewer ≠ approver) | | |
| H8 | **[Blocker]** Dependency CVE scan: zero High+ open at go-live | | |
| H9 | **[Strong]** Container images hardened (distroless or equivalent) | | |
| H10 | **[Strong]** Customer PII access audited; minimised to need-to-know | | |

---

## Section I — Observability

**Owner:** SRE

| # | Item | Status | Evidence |
|---|---|---|---|
| I1 | **[Blocker]** Structured logging across all services with trace ID propagation | | |
| I2 | **[Blocker]** Distributed tracing live; 10% sample non-error, 100% error | | |
| I3 | **[Blocker]** Per-engine metrics dashboard live (latency, throughput, errors, golden pass rate) | | |
| I4 | **[Blocker]** Reasoning-specific dashboard live (tokens, cost, latency, model version, eval pass) | | |
| I5 | **[Blocker]** All alerts have runbooks; runbook links on the alert itself | | |
| I6 | **[Blocker]** SLOs defined per workload; error budget tracking visible | | |
| I7 | **[Strong]** 30 days of metrics retained pre go-live with no gaps | | |

---

## Section J — User Experience

**Owner:** Design + Frontend

| # | Item | Status | Evidence |
|---|---|---|---|
| J1 | **[Blocker]** WCAG 2.1 AA pass (automated + manual review) | | |
| J2 | **[Blocker]** State audit complete per `UI_Polish.md` §3 | | |
| J3 | **[Blocker]** All exports (PDF, Excel, CSV, PNG, SVG) produce well-formed outputs | | |
| J4 | **[Blocker]** Conversational UI conforms to `UI_Polish.md` §6 | | |
| J5 | **[Strong]** Keyboard-only navigation tested for three core flows | | |
| J6 | **[Strong]** Reduced-motion respected throughout | | |
| J7 | **[Strong]** Microcopy review complete | | |

---

## Section K — Workflow & Sign-off

**Owner:** Product + Platform Lead

| # | Item | Status | Evidence |
|---|---|---|---|
| K1 | **[Blocker]** Maker-checker enforced on every filed number; bypass impossible | | |
| K2 | **[Blocker]** Electronic attestation captures user, role, IP, timestamp, content hash | | |
| K3 | **[Blocker]** Close calendar configured with all dependencies and owners | | |
| K4 | **[Blocker]** Distribution channels to regulators tested (out-of-band confirmation) | | |
| K5 | **[Strong]** Workflow notification system tested end-to-end | | |
| K6 | **[Strong]** Sign-off audit trail accessible to internal audit team | | |

---

## Section L — Documentation

**Owner:** All workstream leads

| # | Item | Status | Evidence |
|---|---|---|---|
| L1 | **[Blocker]** Every engine documented (purpose, citation, formula, example, edge cases) | | |
| L2 | **[Blocker]** Every prompt template documented (inputs, outputs, eval set, known failures) | | |
| L3 | **[Blocker]** Operator runbooks for every alert | | |
| L4 | **[Blocker]** User guides for preparer, reviewer, approver roles | | |
| L5 | **[Blocker]** API documentation (OpenAPI) published | | |
| L6 | **[Strong]** New-developer onboarding tested with someone unfamiliar with the platform | | |
| L7 | **[Strong]** Change management procedures documented (new engine, new prompt, new return) | | |

---

## Section M — Compliance & Governance

**Owner:** Head of Compliance

| # | Item | Status | Evidence |
|---|---|---|---|
| M1 | **[Blocker]** Model inventory entry created for every calculation engine; validation status recorded | | |
| M2 | **[Blocker]** LLM usage documented to model risk team as advisory (non-determinative) | | |
| M3 | **[Blocker]** 7-year audit log retention configured (or per jurisdiction requirement) | | |
| M4 | **[Blocker]** Reproducibility of historical filings from snapshot + code version verified | | |
| M5 | **[Blocker]** Regulatory citations current; framework changes since build commencement reviewed | | |
| M6 | **[Strong]** Internal audit walkthrough completed | | |
| M7 | **[Strong]** Independent model validation scheduled for post-go-live cycle | | |

---

## Section N — Demo & Sandbox

**Owner:** Product

| # | Item | Status | Evidence |
|---|---|---|---|
| N1 | **[Strong]** Demo mode runs without external dependencies; isolation verified | | |
| N2 | **[Strong]** Three guided demo tours run cleanly end-to-end | | |
| N3 | **[Strong]** Watermarks present on all demo outputs | | |
| N4 | **[Strong]** Demo tenant cannot reach production via any path (isolation tests pass) | | |
| N5 | **[Strong]** Demo dataset version hash recorded in release notes | | |

---

## Section O — Operational Readiness

**Owner:** SRE + Platform Lead

| # | Item | Status | Evidence |
|---|---|---|---|
| O1 | **[Blocker]** On-call rotation defined for production | | |
| O2 | **[Blocker]** Incident response procedure documented and rehearsed | | |
| O3 | **[Blocker]** Communication plan for incidents (internal + regulator-facing if material) | | |
| O4 | **[Blocker]** Rollback procedure documented and tested for the most recent two releases | | |
| O5 | **[Blocker]** Feature flag system live; tested for incremental rollout and emergency disable | | |
| O6 | **[Strong]** Capacity headroom monitored; scaling thresholds defined | | |
| O7 | **[Strong]** Cost monitoring & alerting live for compute, storage, and LLM API spend | | |

---

## Section P — Go-Live Dry Run

**Owner:** Platform Lead

The dry run is a controlled rehearsal of a full reporting cycle, performed in staging, with all sign-off roles participating.

| # | Item | Status | Evidence |
|---|---|---|---|
| P1 | **[Blocker]** End-to-end reporting cycle dry run completed in staging | | |
| P2 | **[Blocker]** Dry-run regulatory return prepared, reviewed, signed, and (notionally) filed | | |
| P3 | **[Blocker]** All five sign-off roles participated in dry run | | |
| P4 | **[Blocker]** Issues raised in dry run resolved or formally accepted | | |
| P5 | **[Blocker]** Stability window: 30-day green window with no Critical incidents prior to go-live | | |

---

## Sign-off

The platform is approved for production release when every **[Blocker]** above is green, every **[Strong]** is green or formally exempted, and the following sign-offs are recorded:

| Role | Name | Date | Signature / Evidence |
|---|---|---|---|
| Platform Lead | | | |
| Chief Risk Officer | | | |
| Chief Financial Officer | | | |
| Chief Information Security Officer | | | |
| Head of Compliance | | | |

A copy of the completed checklist, with evidence links, is stored immutably in the audit log under the release tag.

---

## Re-Validation Cadence

After go-live, the following items are re-validated on the cadences below. The checklist remains an active document, not an archived one.

| Item | Cadence |
|---|---|
| Determinism CI | Nightly |
| Eval suites | Per release + monthly |
| Golden tests | Per release |
| DR failover drill | Quarterly |
| Penetration test | Annually + post-major-release |
| Backup restore verification | Weekly |
| Audit log chain verification | Daily |
| Cost & capacity review | Monthly |
| Documentation freshness audit | Semi-annually |
| Regulatory citation review | Quarterly |

---

## Companion Documents

- `Final_Build_Pack.md` — overall architecture
- `Repository_Reconciliation.md` — repo consolidation
- `Phase27.md` — productionisation phase
- `Demo_Mode.md` — demo configuration
- `UI_Polish.md` — UI finalisation
- `docs/runbooks/` — operational runbooks
- `docs/incidents/` — incident response procedures

---

*End of Deployment Checklist.*
