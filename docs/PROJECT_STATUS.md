# BSM Platform — Project Status

**Document version:** 2026-06-28  
**Status:** Epic 1 complete and validated. Awaiting approval for Epic 2A.  
**Source of truth:** `build-pack/Final_Build_Pack.md`

---

## 1. Project Overview

The BSM Platform is a regtech + ALM (Asset-Liability Management) system for banks, NBFCs, and large corporate treasuries. It automates regulatory capital, liquidity, and IFRS 9 reporting while providing AI-generated variance commentary, disclosure drafts, and conversational analytics.

The platform is used by bank treasury and regulatory reporting teams to:

- Compute RWA, LCR, NSFR, capital ratios, ECL, ALM gaps, and stress test results
- Generate Pillar 3 disclosures and variance narratives using Claude
- Prepare and file regulatory returns (RBI DSB, FR Y-9C / FFIEC, COREP/FINREP in v2)
- Maintain a tamper-evident audit trail linking every filed number to its source snapshot, function version, and git SHA
- Manage the close calendar with maker-checker segregation of duties

**Target users:** Bank treasury analysts, regulatory reporting teams, CFOs, internal audit.  
**Regulatory coverage (v1):** India (RBI), United States (Federal Reserve / OCC). EU COREP/FINREP deferred to v2.

---

## 2. Vision and Objectives

### Core Principle

> **The LLM never computes regulatory numbers. Python computes them; Claude explains and reasons about them.**

Every number shown to a user or filed with a regulator is traceable to a deterministic Python function with a version hash. Claude operates exclusively as an advisory, explanatory, and drafting layer.

### Strategic Objectives

1. **Auditability** — Any filed number can be reproduced from `snapshot + engine version + git SHA`, bit-identical.
2. **Determinism** — Same inputs always produce identical outputs; hash-verified on every compute run.
3. **SOD enforcement** — Segregation of duties (Preparer ≠ Reviewer ≠ Approver) enforced at the API layer, not just UI.
4. **Tamper evidence** — Append-only, hash-chained audit log with DDL-level protection against UPDATE/DELETE.
5. **Regulatory coverage** — Full Basel III (RWA, capital, LCR, NSFR), IFRS 9 (staging + ECL), IRRBB (EVE, NII), and ALM (gap, FTP) in v1.

---

## 3. Current Architecture

### Two-Layer Contract

```
┌──────────────────────────────────────────────────────────┐
│                     USER INTERFACE                        │
│   (Dashboards, Reports, Conversational UI, Workpapers)   │
└───────────────────────┬──────────────────────────────────┘
                        │
             ┌──────────┴──────────┐
             │                     │
     ┌───────▼────────┐   ┌────────▼──────────┐
     │   REASONING    │   │      COMPUTE       │
     │     LAYER      │◄──┤       LAYER        │
     │   (Claude)     │   │     (Python)       │
     │                │   │                    │
     │ • Explain      │   │ • RWA calculation  │
     │ • Narrate      │   │ • LCR / NSFR       │
     │ • Draft        │   │ • ECL (IFRS 9)     │
     │ • Q&A          │   │ • Capital ratios   │
     │ • Triage       │   │ • ALM gaps / EVE   │
     └────────┬───────┘   └────────┬───────────┘
              │                    │
              └──────────┬─────────┘
                         │
               ┌─────────▼──────────┐
               │   DATA PLATFORM    │
               │  PostgreSQL 16     │
               │  • Positions       │
               │  • Reference data  │
               │  • Snapshots       │
               │  • Audit log       │
               │  • Result tables   │
               └────────────────────┘
```

### Deployment Model

**Modular Monolith:** Single FastAPI service (`apps/api`) that imports all eight compute engines as Python packages at startup. No microservices. Engines are upgraded independently via semantic versioning; the monolith is released as a single deployable unit.

### Import Boundaries (enforced by `import-linter` in CI)

| Rule | Enforced Between |
|------|-----------------|
| Reasoning cannot import engines | `reasoning/*` → `engines/*` blocked |
| Reasoning cannot use numpy/pandas/scipy | `reasoning/*` → numerical libs blocked |
| Engines cannot import reasoning | `engines/*` → `reasoning/*` blocked |
| Engines cannot call Anthropic API | `engines/*` → `anthropic` blocked |
| Reports layer cannot compute | `reports/*` → numpy/pandas/scipy blocked |

### Data Flow

```
Position upload → Snapshot (DRAFT) → Snapshot locked (LOCKED)
    → Compute engines run → ComputeRun stored (inputs_hash + outputs_hash)
    → Reasoning modules read ComputeRun → ReasoningRun stored
    → Workpaper assembled → Maker-checker sign-off → Snapshot filed (FILED)
```

---

## 4. Technology Stack

| Concern | Choice | Version | Rationale |
|---------|--------|---------|-----------|
| API framework | FastAPI | 0.111+ | Typed, async, auto-documented |
| Python runtime | CPython | 3.12 | Numerical libraries, regulatory community standard |
| Package manager | uv | 0.11.25 | Workspace monorepo management |
| Database | PostgreSQL | 16 | ACID, range partitioning, DDL triggers |
| ORM / migrations | SQLAlchemy 2.0 + Alembic | 2.0 / 1.13 | Async, typed mapped columns |
| DB driver | asyncpg | 0.29+ | Native async PostgreSQL |
| Validation | Pydantic v2 | 2.7+ | Frozen models, strict typing at boundaries |
| Frontend | React + TypeScript | 18.3 / 5.5 | Standard |
| Frontend build | Vite | 5.3 | Fast dev server, ES2022 output |
| Frontend styling | Tailwind CSS | 3.4 | Design token system |
| Frontend state | TanStack Query | 5.45 | Server state management |
| Charts | Recharts | 2.12 | Standard chart library |
| AI / Reasoning | Anthropic Claude API | claude-sonnet-4-6 | Pinned; change requires full eval re-run |
| Auth | OIDC (Okta / Azure AD) | — | Enterprise standard (Epic 5+) |
| Audit log | Append-only + hash chain | — | DDL-level tamper evidence |
| Observability | OpenTelemetry | 1.25+ | Traces, metrics, logs |
| Structured logging | structlog | 24.2+ | Machine-readable JSON logs |
| Container | Docker + Compose | — | Multi-stage build; non-root production user |
| CI/CD | GitHub Actions | — | 7 CI jobs + 4 nightly jobs |
| Python linting | ruff | — | Replaces flake8 + isort + pyupgrade |
| Type checking | mypy (strict) | — | `--strict` on `shared/` and `apps/api/app/` |
| Frontend linting | ESLint v9 flat config | — | TypeScript-strict, react-hooks |
| Secret detection | gitleaks | — | Pre-commit + CI |

---

## 5. Repository Structure

```
frbsm-platform/
├── apps/
│   ├── api/                    FastAPI modular monolith
│   │   ├── alembic/            20 migrations (0001→0020)
│   │   ├── alembic/versions/   All reversible; linear chain
│   │   ├── app/
│   │   │   ├── config.py       Settings; Claude model pinned
│   │   │   ├── main.py         App factory; /health, /health/db
│   │   │   └── db/
│   │   │       ├── base.py     DeclarativeBase, mixins
│   │   │       ├── session.py  Async sessionmaker
│   │   │       └── models/     8 ORM models; imported by Alembic
│   │   └── Dockerfile          4-stage: base→builder→dev→prod
│   │
│   ├── web/                    React 18 + TypeScript SPA
│   │   ├── src/
│   │   │   ├── main.tsx        StrictMode React root
│   │   │   └── App.tsx         QueryClientProvider shell
│   │   ├── vite.config.ts      @/* alias, /api proxy
│   │   ├── tailwind.config.ts  Design tokens
│   │   └── Dockerfile          dev (Vite) + prod (nginx)
│   │
│   └── workers/                Background task workers (stub; Epic 5+)
│
├── engines/                    8 compute engines (Python stubs)
│   ├── rwa/                    Risk-Weighted Assets
│   ├── capital/                CET1 / Tier 1 / Total Capital
│   ├── liquidity/              LCR / NSFR
│   ├── irrbb/                  EVE / NII sensitivity
│   ├── ecl/                    Expected Credit Loss (IFRS 9)
│   ├── alm/                    ALM gap analysis
│   ├── ftp/                    Funds Transfer Pricing
│   └── stress/                 Stress testing
│
├── reasoning/                  Claude reasoning modules (stubs)
│   ├── prompts/_schema.json    JSON Schema all templates must satisfy
│   ├── variance/               Period-over-period commentary
│   ├── disclosures/            Pillar 3 drafting
│   ├── conversational/         Natural language Q&A
│   └── triage/                 Alert classification
│
├── shared/                     Installable Python packages
│   ├── domain/                 Frozen Pydantic v2 domain models
│   │   └── domain/
│   │       ├── enums.py        All platform enumerations
│   │       ├── position.py     Position + Collateral (with composite FK field)
│   │       ├── snapshot.py     Snapshot (DRAFT→LOCKED→FILED lifecycle)
│   │       ├── compute.py      ComputeRun + EngineVersion
│   │       ├── reasoning.py    ReasoningOutput + ReasoningRun
│   │       └── reference_data.py  RiskWeight, YieldCurve, etc.
│   ├── audit/                  Hash-chain audit log writer
│   ├── testing/                Shared pytest fixtures
│   └── utils/                  Decimal / date helpers
│
├── tests/
│   ├── unit/                   13 passing tests; no I/O
│   ├── integration/            Schema + FK + trigger tests (requires PostgreSQL)
│   ├── golden/                 Determinism / regulator-example tests
│   ├── property/               Hypothesis invariant tests
│   ├── e2e/                    Full-stack HTTP tests
│   ├── determinism/            Nightly hash-stability checks
│   └── eval_harness/           Reasoning module quality (nightly, gated)
│
├── reports/                    Report assemblers (stubs)
├── workflow/                   Maker-checker state machine (stub)
├── observability/              OpenTelemetry configuration (stub)
├── data/demo/                  Generated demo data (not committed)
├── ops/
│   ├── postgres/init.sql       DB-level init: pgcrypto, UTC, bsm_app role
│   └── demo_tenants.yaml       Demo tenant definitions (IN + US)
├── docs/                       Documentation
├── tools/                      Developer tooling scripts
│
├── pyproject.toml              uv workspace root; ruff/mypy/pytest/import-linter
├── uv.lock                     Locked dependency tree (121 packages)
├── pnpm-workspace.yaml         Frontend workspace root
├── docker-compose.yml          PostgreSQL 16 + API + Web dev stack
├── ruff.toml                   Python lint rules
├── .pre-commit-config.yaml     ruff, mypy, gitleaks hooks
└── .github/workflows/
    ├── ci.yml                  7 jobs on every PR
    └── nightly.yml             4 jobs (determinism, property, eval, e2e)
```

**Total tracked files:** 135

---

## 6. Completed Epics

### Epic 0 — Repository Foundation
**Commits:** `727352a`  
**Branch:** `main`

Full monorepo scaffold created from scratch:

- uv Python workspace with 6 members (shared/domain, shared/audit, shared/testing, shared/utils, apps/api, apps/workers)
- FastAPI application skeleton with async SQLAlchemy 2.0, Alembic, Pydantic v2 settings, lifespan management
- React 18 + TypeScript 5 frontend with Vite, Tailwind CSS, TanStack Query
- Docker Compose dev stack (PostgreSQL 16, API, Web)
- Multi-stage Dockerfiles (base→builder→development→production) for both API and web
- GitHub Actions CI (7 jobs) and nightly workflow (4 jobs)
- Import boundary enforcement via `import-linter` (5 contracts)
- Pre-commit hooks: ruff, mypy, gitleaks, standard file checks
- All configuration files: `pyproject.toml`, `ruff.toml`, `uv.lock`, `pnpm-workspace.yaml`
- Frozen Pydantic v2 domain models: Position, Collateral, Snapshot, ComputeRun, ReasoningOutput, ReferenceData enums
- All 8 compute engine stubs and 4 reasoning module stubs
- Test suite scaffolding: unit, integration, golden, property, e2e, determinism, eval harness conftest files
- Documentation: `README.md`, `docs/ARCHITECTURE.md`, `docs/contributing/code_review.md`, `data/demo/README.md`
- Ops: `ops/postgres/init.sql`, `ops/demo_tenants.yaml`

### Epic 1 — Database Foundation
**Commits:** `e11aa1f` (complete), `f0c0367` (validated)  
**Branch:** `main` (merged from `epic-1-database`)  
**Tag:** `v0.1-database-foundation`

20 Alembic migrations creating the complete PostgreSQL schema:

| Migration | Description |
|-----------|-------------|
| 0001 | Counterparties, positions (unpartitioned), collateral |
| 0002 | Reference data: risk weights, HQLA haircuts, run-off rates, CCFs, yield curves |
| 0003 | Snapshots: point-in-time frozen data |
| 0004 | Compute runs: audit record for every engine invocation |
| 0005 | Reasoning runs: audit trail for Claude invocations |
| 0006 | Audit log: append-only, hash-chained with DDL immutability trigger |
| 0007 | Workflow: workpapers, sign-offs, close calendar tasks |
| 0008 | Positions re-created as range-partitioned table (by `reporting_date`); collateral gains composite FK |
| 0009 | Legal entities and entity-level capital requirements |
| 0010 | Product catalog: product groups, products, behavioural assumptions |
| 0011 | Cashflows and cashflow projections (range-partitioned by `cashflow_date`) |
| 0012 | Balance sheet line items and summaries |
| 0013 | LCR result tables (with HQLA, inflow, outflow components) |
| 0014 | NSFR result tables (ASF and RSF components) |
| 0015 | Capital adequacy result table (CET1, Tier 1, Total Capital, RWA, ratios) |
| 0016 | Scenario management: scenario definitions and parameter sets |
| 0017 | Stress testing: runs, results, position-level impacts |
| 0018 | Structural Liquidity Statement (SLS / RBI DSB-II) |
| 0019 | Regulatory parameter history, filings, and filing lineage |
| 0020 | Demo seed data: 12 counterparties, 30 positions, 5 scenarios, reference data |

---

## 7. Validation Results

Comprehensive database validation was performed after Epic 1 (2026-06-28):

| Validation | Result | Detail |
|------------|--------|--------|
| Migration chain integrity | PASS | Linear 0001→0020; no gaps; no branches |
| Full downgrade → upgrade cycle | PASS | All 20 migrations reversed cleanly to base, re-applied to head |
| Tables present (Final Build Pack §4) | PASS | All 24 required entities present |
| Total tables | PASS | 65 tables |
| Foreign keys | PASS | 96 FKs; all RESTRICT or CASCADE; no unexpected rules |
| Indexes | PASS | 293 indexes |
| Partitioning (positions + cashflows) | PASS | RANGE by date; 11 annual + 1 DEFAULT partition each |
| Audit log immutability | PASS | DDL trigger blocks UPDATE and DELETE at DB level |
| Hash-chain fields | PASS | `entry_hash` + `prev_hash` on every audit log entry |
| Demo seed data | PASS | 12 counterparties, 30 positions, 5 scenarios, reference data |
| Snapshot hash integrity | PASS | `position_hash` and `reference_hash` are valid 64-char hex |
| Unit tests (13/13) | PASS | Domain model round-trip, constraints, snapshot lifecycle |
| ORM / migration sync | PASS | After fixing 3 discrepancies (see Known Technical Debt §12) |

**Bugs found and fixed during validation (7 total):**

1. `Snapshot` domain model: `reporting_date_iso: str` → `reporting_date: date`
2. `Collateral` domain model: added missing `position_reporting_date: date` for composite FK
3. `PositionModel` ORM: composite PK `(id, reporting_date)` was not declared — used `UUIDPrimaryKeyMixin` (single-column PK only)
4. Unit test fixtures: wrong field names throughout (`position_id`, `carrying_value`, `rating_grade`, etc.)
5. `pyproject.toml`: missing `[tool.uv.sources]` — workspace cross-references unresolved; `uv lock` failed
6. Missing `uv.lock`: generated and committed; Dockerfiles updated to `--all-packages`
7. Migration 0020 downgrade: `LIKE` on UUID columns fails — fixed with `::text` cast

---

## 8. Current Git Branches

| Branch | Status | Description |
|--------|--------|-------------|
| `main` | Active | All work merged; current HEAD is `f0c0367` |
| `epic-1-database` | Merged | Epic 1 development branch; merged to main, retained remotely |

---

## 9. Release Tags

| Tag | Commit | Date | Description |
|-----|--------|------|-------------|
| `v0.1-database-foundation` | `f0c0367` | 2026-06-28 | Epic 1 Database Foundation — validated and complete |

---

## 10. Outstanding Work

The following was scoped for v1 but not yet started:

### Compute Engines (all stubs — no business logic)
- `engines/rwa/` — RWA credit SA, IRB-F, market risk SA, operational risk BIA/SA-OR
- `engines/capital/` — CET1, Tier 1, Total Capital, conservation/countercyclical buffers
- `engines/liquidity/` — LCR (HQLA, outflows, inflows), NSFR (ASF, RSF)
- `engines/irrbb/` — EVE and NII sensitivity (6 BCBS shocks), repricing gap
- `engines/ecl/` — IFRS 9 staging (SICR rules), ECL (PD × LGD × EAD × discount)
- `engines/alm/` — Gap analysis, behavioural maturity overlays
- `engines/ftp/` — Matched-maturity FTP, liquidity premium
- `engines/stress/` — Regulatory and internal scenario application

### Reasoning Modules (all stubs — no prompt logic)
- `reasoning/variance/` — Period-over-period commentary generator
- `reasoning/disclosures/` — Pillar 3 quantitative + qualitative drafting
- `reasoning/conversational/` — Natural language Q&A over compute outputs
- `reasoning/triage/` — Alert classification and reconciliation break explanation

### API Layer (no endpoints yet)
- Position ingestion API (upload, validate, stage)
- Snapshot management (create, lock, file)
- Engine trigger endpoints (run RWA, run LCR, etc.)
- Workpaper assembly and sign-off API
- User management and OIDC integration
- WebSocket / SSE for long-running engine progress

### Frontend (scaffold only — no screens)
- Authentication flow (OIDC)
- Dashboard: capital ratios, LCR, NSFR dials
- Position viewer and uploader
- Snapshot manager
- Compute run history
- Workpaper view and sign-off
- Variance commentary display
- Conversational analytics chat interface
- Regulatory filing preparation wizard

### Infrastructure
- OIDC integration (Okta / Azure AD)
- Object storage for snapshot binaries (S3 / GCS)
- Secret management (HashiCorp Vault / AWS Secrets Manager)
- TLS termination in production nginx
- Horizontal scaling configuration for API workers

---

## 11. Next Implementation Milestones

### Epic 2A — Data Ingestion Layer
**Objective:** Accept position and reference data uploads; validate; create and lock snapshots.

Deliverables:
- Position upload API (CSV/Excel → validated `Position` domain models)
- Reference data API (risk weights, haircuts, run-off rates, CCFs, yield curves)
- Snapshot creation and locking logic (SHA-256 content hashing)
- Audit log entries for every state change
- Unit + integration tests for all endpoints

### Epic 2B — Snapshot Engine
**Objective:** Implement the freeze-and-hash mechanism that is the contract between data and compute.

Deliverables:
- Snapshot freeze service: serialises positions + reference data, computes SHA-256 hashes
- Snapshot status machine: DRAFT → LOCKED (one-way; no rollback)
- Position retrieval from frozen snapshot (deterministic ordering for hash consistency)
- Golden test: same snapshot content always produces same hash

### Epic 3 — RWA Engine (Credit SA)
**Objective:** First compute engine: Basel III Standardised Approach credit risk-weighted assets.

Deliverables:
- `engines/rwa/credit_sa.py`: asset class → risk weight lookup → RWA computation
- Golden tests against published RBI / BCBS worked examples
- Property tests: RWA ≥ 0, RWA ≤ notional × 1250% (maximum risk weight)
- Determinism test: same snapshot → same RWA hash
- Full audit log integration (inputs_hash, outputs_hash, engine version, git SHA)

### Epic 4 — Capital Engine
**Objective:** CET1, Tier 1, and Total Capital ratios derived from RWA output.

### Epic 5 — LCR Engine
**Objective:** LCR computation: HQLA stock, stressed net cash outflows, ratio.

### Epic 6 — API Layer (Phase 1)
**Objective:** REST endpoints wiring data ingestion, snapshot, RWA, and capital compute to the frontend.

---

## 12. Known Technical Debt

| Item | Severity | Location | Description |
|------|----------|----------|-------------|
| Port 5432 conflict (local development) | Low | Dev environment | Local PostgreSQL intercepts `localhost:5432`; Alembic/asyncpg from host must use Docker network. See `dev_environment.md` in memory. |
| `apps/workers` | Low | `apps/workers/` | Stub only; no worker framework (Prefect/Airflow) integrated yet |
| COREP/FINREP | Deferred | `reports/regulatory/` | EU regulatory returns deferred to v2; `ReturnRegistry` extensibility preserved |
| IRB-A (advanced) | Deferred | `engines/rwa/` | Only SA and IRB-F in v1; IRB-A deferred to v2 |
| FRTB | Deferred | `engines/rwa/` | Fundamental Review of Trading Book deferred to v2 |
| OIDC integration | Pending | `apps/api/app/auth/` | Auth routes not yet wired; placeholder `python-jose` dependency in place |
| Object storage | Pending | `data/snapshot/` | Snapshot binaries currently in PostgreSQL; S3/GCS integration needed for production |
| Reasoning eval harness | Pending | `tests/eval_harness/` | 500-case golden eval set for 4 reasoning modules defined in spec but not yet populated |
| `pnpm-lock.yaml` | Pending | repo root | Frontend lockfile not yet generated; `pnpm install` required before first frontend CI run |
| `apps/web` router | Pending | `apps/web/src/App.tsx` | React Router not yet mounted; `App.tsx` is a placeholder shell |

---

## 13. Current Implementation Status

### Layer-by-layer completion

| Layer | Status | Notes |
|-------|--------|-------|
| **Database schema** | Complete | 65 tables, 20 migrations, validated |
| **Domain models** | Complete | 7 frozen Pydantic v2 model files in `shared/domain` |
| **ORM models** | Complete | 8 SQLAlchemy 2.0 models in `apps/api/app/db/models/` |
| **Compute engines** | Not started | 8 stub directories; `__init__.py` only |
| **Reasoning modules** | Not started | 4 stub directories; prompt schema defined |
| **API endpoints** | Not started | `app/main.py` has only `/health` and `/health/db` |
| **Frontend screens** | Not started | `App.tsx` is a placeholder; no routes |
| **Auth / OIDC** | Not started | Dependency included; no routes implemented |
| **Workflow** | Not started | DB tables exist; no business logic |
| **Audit log writer** | Not started | `shared/audit/` stub; DB trigger exists |
| **Observability** | Not started | `observability/` stub; OTel wired in dependencies only |
| **CI/CD** | Complete | 7 CI + 4 nightly jobs defined |
| **Docker** | Complete | Multi-stage builds; `uv.lock` committed |
| **Test infrastructure** | Complete | Conftest files for all 7 test suites |
| **Unit tests** | 13 tests | Domain model validation; all passing |
| **Integration tests** | Framework ready | Schema + FK + trigger tests written; requires live PostgreSQL |
| **Golden tests** | Framework ready | Fixture loader written; no fixtures yet (engines not built) |

### Percentage complete (by Epic count, not effort)

```
Foundation (Epics 0–1):   ████████████████████  2 / 2   100%
Core engines (Epics 2–8): ░░░░░░░░░░░░░░░░░░░░  0 / 7     0%
Reasoning (Epics 9–11):   ░░░░░░░░░░░░░░░░░░░░  0 / 3     0%
UI / API (Epics 12–14):   ░░░░░░░░░░░░░░░░░░░░  0 / 3     0%
Production (Epic 15):     ░░░░░░░░░░░░░░░░░░░░  0 / 1     0%
────────────────────────────────────────────────────────
Overall:                                         2 / 16   12.5%
```

---

## 14. Remaining Roadmap to MVP

MVP is defined as: a single bank can upload positions, run RWA + capital + LCR + NSFR, view results, and export a workpaper for human sign-off — with full audit trail.

| Epic | Scope | Est. Sprints |
|------|-------|--------------|
| 2A | Data ingestion API (position + reference data upload, validation) | 2 |
| 2B | Snapshot engine (freeze, hash, lock) | 1 |
| 3 | RWA engine — Credit SA (Basel III standardised approach) | 2 |
| 4 | Capital engine (CET1, Tier 1, Total Capital, buffers) | 2 |
| 5 | LCR engine (HQLA, outflows, inflows) | 2 |
| 6 | API endpoints — Phase 1 (ingest, snapshot, RWA, capital, LCR) | 2 |
| 7 | Frontend — Phase 1 (auth, dashboard, position upload, ratio dials) | 3 |
| 8 | Workflow — Phase 1 (workpaper assembly, maker-checker sign-off) | 2 |
| 9 | Reasoning — Variance commentary (first reasoning module) | 2 |
| 10 | Integration hardening (e2e tests, golden tests for all engines) | 2 |
| **MVP Total** | | **~20 sprints** |

---

## 15. Remaining Roadmap to Production

Production requires MVP plus the following:

| Phase | Scope |
|-------|-------|
| NSFR engine | Net Stable Funding Ratio (ASF, RSF) |
| IRRBB engine | EVE and NII sensitivity, 6 BCBS shocks |
| IFRS 9 engine | Staging (SICR) + ECL (PD × LGD × EAD) |
| ALM engine | Gap analysis, behavioural maturity, FTP |
| Stress testing engine | Regulatory + internal scenario shock application |
| Reasoning — Disclosures | Pillar 3 quantitative + qualitative drafting |
| Reasoning — Conversational | Natural language Q&A interface |
| Reasoning — Triage | Alert classification and reconciliation breaks |
| Frontend — Phase 2 | Full workpaper, regulatory return wizard, conversational UI |
| API — Phase 2 | Remaining engine endpoints, WebSocket progress, filing export |
| OIDC / Auth | Okta / Azure AD integration, session management |
| Object storage | S3/GCS for snapshot binaries (production scale) |
| Observability | Full OpenTelemetry pipeline → Datadog / Grafana dashboards |
| Phase 27 — Production hardening | Reasoning audit, determinism proof, DR testing, security hardening, performance SLA validation |
| COREP/FINREP (v2) | EU regulatory returns, ReturnRegistry extensibility |

**Phase 27 (Final productionisation)** per `build-pack/Phase27.md` is a standalone phase covering:
- Reasoning layer boundary audit + eval harness (500+ cases, ≥95% pass rate)
- Historical reproduction test (12 months of filings, bit-identical)
- Security hardening (pen test, vault integration, TLS enforcement)
- Performance validation against SLAs (LCR ≤ 5 min, capital ≤ 30 min, Q&A ≤ 3s)
- Disaster recovery drill and runbooks
- Deployment checklist sign-off (`build-pack/Deployment_Checklist.md`)

---

*This document is updated at the start and end of each Epic. For the authoritative feature specification, refer to `build-pack/Final_Build_Pack.md`. For architectural constraints, see `docs/ARCHITECTURE.md`. For development environment quirks, see the memory index at `.claude/projects/.../memory/MEMORY.md`.*
