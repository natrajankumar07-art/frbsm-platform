# Phase 27 — Productionisation

**Phase Number:** 27 (Final)
**Predecessors:** Phases 1–26 complete and gated
**Status:** In-progress
**Exit Criterion:** Platform passes `Deployment_Checklist.md` end-to-end

---

## 1. Purpose of Phase 27

Phases 1–26 deliver functionality. Phase 27 makes the platform **production-grade**: hardened, observable, recoverable, performant under realistic load, and ready for regulator scrutiny.

Phase 27 introduces no new calculation engines and no new reasoning modules. Anything that would add functionality belongs in v1.1 or later. Phase 27 is exclusively about **non-functional readiness**.

The phase is decomposed into nine workstreams. All run in parallel; all must close before go-live.

---

## 2. Workstream A — Reasoning Layer Hardening

### 2.1 Objectives

The reasoning layer (Claude) has been integrated incrementally across earlier phases. Phase 27 audits it end-to-end against the architectural contract in `Final_Build_Pack.md` §2 and §8.

### 2.2 Deliverables

- **Boundary audit report:** review of every `reasoning/*` module to confirm no numerical computation, no banned imports, no fabricated values
- **Prompt registry:** every prompt template extracted into versioned templates under `reasoning/prompts/`, each with: purpose, expected inputs schema, expected outputs schema, evaluation set
- **Eval harness:** golden eval set of 500+ cases for the four production reasoning modules (variance, disclosures, conversational, triage). Each case has: structured input, gold response or response schema, scoring rubric.
- **Model pinning:** explicit model version pinned in config, with documented upgrade procedure
- **PII scrubber:** confirmed that no PII reaches prompts; tokenised references only
- **Cost & latency budget:** per-module budget set, alerts when exceeded
- **Disagreement protocol:** procedure for when reasoning output contradicts compute output — compute always wins; reasoning output flagged for review

### 2.3 Acceptance

- Eval suite passes at ≥95% on golden cases
- Zero boundary violations in CI
- Prompt registry covers 100% of production reasoning calls
- Model version change cannot ship without eval suite re-run

---

## 3. Workstream B — Determinism & Reproducibility

### 3.1 Objectives

Every regulatory number, on demand, must be reproducible from a snapshot plus code version. Phase 27 proves this end-to-end against historical data.

### 3.2 Deliverables

- **Historical reproduction test:** the last 12 months of filed regulatory returns reproduced from archived snapshots, bit-identical to what was filed
- **Snapshot integrity verification:** all snapshots in cold storage validated against their content hash
- **Code version lineage:** every audit log entry references engine version + git SHA; lookup tool that, given a filed number, returns the snapshot, function, and SHA that produced it
- **Determinism CI job:** nightly job that re-runs a fixed set of snapshots and compares outputs; any divergence blocks release

### 3.3 Acceptance

- 12-month historical reproduction: 100% bit-identical
- Determinism CI green for 30 consecutive nights pre go-live
- Lineage tool returns answer within 5 seconds for any filed number

---

## 4. Workstream C — Performance & Capacity

### 4.1 Objectives

Validate the SLAs in `Final_Build_Pack.md` §10 under realistic production load.

### 4.2 Load Profile

| Workload | Concurrency | Volume |
|---|---|---|
| Daily LCR runs | 1 at peak | Full bank: ~5M positions |
| Monthly capital runs | 1 at month-end | Full bank consolidated |
| Conversational queries | up to 50 concurrent users | 1000 queries/hour at peak |
| Variance narratives | 200 in parallel at month-end | One per ALCO line |
| Snapshot freezes | 5 per day | Each ~5M positions |

### 4.3 Deliverables

- **Load test report:** all SLAs met at 1.5x expected peak
- **Profiling baseline:** flame graphs for the five slowest engines; documented hot paths
- **Capacity plan:** infrastructure sizing for production, with headroom calculations
- **Backpressure policy:** behaviour when conversational queue saturates (queue with timeout, not drop)
- **Async batching:** variance narrative generation batched to amortise LLM call overhead

### 4.4 Acceptance

- All SLAs met at 1.5x peak in load test
- p99 latency within hard limits in `Final_Build_Pack.md` §10
- No memory leaks observed in 72-hour soak test

---

## 5. Workstream D — Disaster Recovery & Business Continuity

### 5.1 Objectives

The platform produces filings on regulator-imposed deadlines. Outages have direct regulatory consequences. Phase 27 builds tested DR.

### 5.2 Deliverables

- **RTO/RPO targets** set per workload:

| Workload | RTO | RPO |
|---|---|---|
| Daily LCR | 4 hours | 1 hour |
| Monthly capital | 24 hours | 4 hours |
| Conversational UI | 4 hours | N/A (stateless) |
| Audit log | 1 hour | 0 (must not lose) |

- **Cross-region replication:** PostgreSQL streaming replication to secondary region; S3 cross-region replication for snapshots
- **Failover drill:** quarterly full failover with measured RTO/RPO; published runbook
- **Audit log durability:** synchronous replication for audit log writes; chosen over latency where they conflict
- **Backup verification:** weekly restore-and-validate of backups
- **Data corruption recovery:** procedure for restoring a corrupted snapshot from cold backup

### 5.3 Acceptance

- Failover drill completed; RTO/RPO targets met
- Restore-from-backup verified weekly for 4 weeks pre go-live
- Runbooks published and rehearsed

---

## 6. Workstream E — Security Hardening

### 6.1 Deliverables

- **Penetration test:** third-party pen test of API, web, and infrastructure; all High/Critical findings remediated, Medium tracked
- **Threat model:** STRIDE analysis covering data exfiltration, privilege escalation, audit tamper, LLM-specific risks (prompt injection, output manipulation)
- **Secrets management:** all secrets in Vault; no secrets in code, config files, or environment variables
- **Audit log tamper-evidence:** hash-chained, append-only audit log; verification job
- **Prompt injection defences:** structured inputs to LLM, output schema validation, no execution of LLM outputs
- **Output review for external-bound content:** any reasoning output destined for a regulator, customer, or auditor requires human sign-off; enforced in workflow
- **Dependency scanning:** all dependencies scanned daily; CVEs of severity High+ block release
- **Container image hardening:** distroless or minimal base images; no shells in production containers

### 6.2 Acceptance

- Pen test report: zero Critical, zero High open at go-live
- Threat model reviewed and signed off
- Audit log verification job runs daily; chain unbroken for ≥30 days pre go-live

---

## 7. Workstream F — Observability

### 7.1 Deliverables

- **Structured logging:** every service emits structured JSON logs with trace ID, span ID, user ID (where applicable), action
- **Distributed tracing:** OpenTelemetry across API, engines, reasoning, workers; sampled at 10% for non-error traces, 100% for errors
- **Metrics:** per-engine: latency (p50/p95/p99), throughput, error rate, golden test pass rate
- **Reasoning-specific metrics:** tokens in/out, cost, latency, model version, eval pass rate, output review acceptance rate
- **Dashboards:** four standard dashboards — Platform Health, Engine Performance, Reasoning Quality, Business KPIs
- **Alerting:** alert rules with documented runbooks for each; no alert without a runbook
- **SLO definitions:** explicit SLOs per workload; error budget tracking

### 7.2 Acceptance

- All four dashboards live; reviewed in dry-run go-live rehearsal
- Every alert has a runbook in `docs/runbooks/`
- 30 days of metrics collected pre go-live with no gaps

---

## 8. Workstream G — User Experience Finalisation

### 8.1 Scope

UI polish is documented in detail in `UI_Polish.md`. Phase 27 incorporates that work and adds:

### 8.2 Deliverables

- **Accessibility audit:** WCAG 2.1 AA compliance verified by automated tooling and manual review
- **Empty states, error states, loading states:** complete coverage per `UI_Polish.md`
- **Print stylesheets:** all reports printable to PDF without UI chrome
- **Keyboard navigation:** primary workflows operable without mouse
- **Internationalisation readiness:** strings externalised; date, number, currency formatting via locale; v1 ships en-IN and en-US

### 8.3 Acceptance

- WCAG 2.1 AA: pass
- Keyboard-only navigation tested for core flows
- All states (empty/loading/error) implemented per design spec

---

## 9. Workstream H — Documentation & Runbooks

### 9.1 Deliverables

- **User documentation:** preparer, reviewer, approver guides; conversational UI primer
- **Operator runbooks:** one per alert; cover diagnosis steps and remediation
- **API documentation:** OpenAPI spec published; examples for each endpoint
- **Calculation documentation:** for every engine — purpose, regulatory citation, formula in LaTeX, worked example, edge cases
- **Reasoning documentation:** for every prompt template — purpose, inputs, outputs, evaluation set, known failure modes
- **Onboarding documentation:** new-developer setup, monorepo conventions, contribution guide
- **Change management documentation:** how to add a new engine, how to add a new prompt, how to add a new regulatory return

### 9.2 Acceptance

- 100% of engines and prompts documented
- Every alert in §7.1 has a runbook
- New-developer onboarding tested with a colleague unfamiliar with the platform

---

## 10. Workstream I — Demo & Sandbox

### 10.1 Scope

Detailed specification in `Demo_Mode.md`. Phase 27 wraps demo mode in:

### 10.2 Deliverables

- Production-quality demo dataset (synthetic, realistic)
- Reset mechanism
- Sandbox tenant isolation
- Guided tour scripts

### 10.3 Acceptance

- Demo mode runs without external dependencies (no real customer data)
- Sandbox cannot leak to production via any path

---

## 11. Cross-Workstream Dependencies

```
B (Determinism) ──┐
                  ├──► Required for go-live sign-off
A (Reasoning) ────┤
                  │
C (Performance) ──┤
                  │
D (DR) ───────────┤
                  │
E (Security) ─────┤
                  │
F (Observability) ┤
                  │
G (UX) ───────────┤
                  │
H (Docs) ─────────┤
                  │
I (Demo) ─────────┘
```

All nine workstreams are required for sign-off; none can be deferred to post-go-live.

---

## 12. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Determinism breaks during reconciliation | Medium | High | Determinism CI runs nightly; failure blocks merges |
| Reasoning eval regression after model upgrade | Medium | High | Eval suite required pre upgrade; rollback documented |
| Load test reveals architectural bottleneck | Medium | High | Run load tests in week 1 of phase, not week 6 |
| Security pen test surfaces blocker | Medium | High | Engage pen test team in week 1, not week 6 |
| Audit log chain breaks under load | Low | Critical | Synthetic load test on audit log specifically |
| DR drill fails to meet RTO | Medium | Medium | Quarterly drills started months before go-live |

---

## 13. Phase 27 Exit Criteria

Phase 27 exits, and the platform is approved for go-live, when:

1. All nine workstream acceptance criteria met
2. Full `Deployment_Checklist.md` walked through and signed off
3. 30-day stability window: nightly determinism CI green, no Critical incidents
4. Regulator-facing dry run: a complete return prepared end-to-end and reviewed (not filed) by relevant SMEs
5. Sign-off from: Platform Lead, CRO designate, CFO designate, CISO, Head of Compliance

---

## 14. What Phase 27 Does Not Do

- No new engines (deferred to v1.1+)
- No new reasoning modules (deferred to v1.1+)
- No new regulatory returns beyond the v1 set (deferred to v1.1+)
- No new jurisdictions beyond IN and US (deferred to v1.1+)

If a stakeholder requests new functionality during Phase 27, the request is logged in the v1.1 backlog and explicitly out of scope.

---

## 15. Companion Documents

- `Final_Build_Pack.md` — phase index and architecture
- `Repository_Reconciliation.md` — repo consolidation (Phase 26 prerequisite)
- `Demo_Mode.md` — sandbox specification (Workstream I)
- `UI_Polish.md` — UX finalisation (Workstream G)
- `Deployment_Checklist.md` — go-live gate

---

*End of Phase 27 specification.*
