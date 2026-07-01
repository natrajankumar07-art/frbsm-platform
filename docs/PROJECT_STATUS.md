# BSM Platform — Project Status

**Document version:** 2026-07-01  
**Status:** Epics 0, 1, 2A, 2B, 2C, 3, 3.1, 4A, 4B, 4C, 4D, 4D.1, and 5 complete. Awaiting approval before Epic 6.  
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

**Modular Monolith:** Single FastAPI service (`apps/api`) that imports all compute engines as Python packages at startup. No microservices. Engines are upgraded independently via semantic versioning; the monolith is released as a single deployable unit.

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
| API framework | FastAPI | 0.138.1 | Typed, async, auto-documented |
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
│   │   │   ├── routers/        9 domain routers + analytics router
│   │   │   ├── services/       9 domain service modules
│   │   │   ├── repositories/   9 domain repository modules
│   │   │   ├── schemas/        9 domain schema modules
│   │   │   └── db/
│   │   │       ├── base.py     DeclarativeBase, mixins
│   │   │       ├── session.py  Async sessionmaker
│   │   │       └── models/     ORM models; imported by Alembic
│   │   └── Dockerfile          4-stage: base→builder→dev→prod
│   │
│   ├── web/                    React 18 + TypeScript SPA (implemented)
│   │   ├── src/
│   │   │   ├── main.tsx        StrictMode React root
│   │   │   ├── App.tsx         React Router + QueryClientProvider
│   │   │   ├── pages/          7 pages (Dashboard, Login, analytics, positions, scenarios)
│   │   │   ├── components/     Layout (AppShell, Sidebar, TopBar) + UI primitives
│   │   │   ├── context/        AuthContext, EntityContext
│   │   │   ├── lib/api.ts      Typed API client
│   │   │   └── types/api.ts    Shared API types
│   │   ├── vite.config.ts      @/* alias, /api proxy to port 8000
│   │   ├── tailwind.config.ts  Design tokens
│   │   └── Dockerfile          dev (Vite) + prod (nginx)
│   │
│   └── workers/                Background task workers (stub; Epic 5+)
│
├── engines/                    9 compute engines (all implemented)
│   ├── common/                 Shared: models.py, audit.py, utils.py
│   ├── liquidity/              LCR, NSFR, SLS engines
│   ├── capital/                Capital Summary engine
│   ├── balance_sheet/          Balance Sheet engine
│   ├── alm/                    Cashflow + Liquidity Gap engines
│   └── stress/                 Scenario + Stress Test engines
│
├── reasoning/                  Claude reasoning modules (stubs — Epic 4)
│   ├── prompts/_schema.json    JSON Schema all templates must satisfy
│   ├── variance/               Period-over-period commentary
│   ├── disclosures/            Pillar 3 drafting
│   ├── conversational/         Natural language Q&A
│   └── triage/                 Alert classification
│
├── shared/                     Installable Python packages
│   ├── domain/                 Frozen Pydantic v2 domain models
│   ├── audit/                  Hash-chain audit log writer
│   ├── testing/                Shared pytest fixtures
│   └── utils/                  Decimal / date helpers
│
├── tests/
│   ├── unit/engines/           126 engine unit tests (all passing)
│   ├── unit/                   Domain model tests (all passing)
│   ├── integration/            Schema + FK + trigger tests (requires PostgreSQL)
│   ├── golden/                 Determinism / regulator-example tests
│   ├── property/               Hypothesis invariant tests
│   ├── e2e/                    Full-stack HTTP tests
│   ├── determinism/            Nightly hash-stability checks
│   └── eval_harness/           Reasoning module quality (nightly, gated)
│
├── docs/
│   ├── engine_validation_report_epic2c.md  Engine Validation Report
│   └── frontend_validation_report_epic3.md Frontend Validation Report
│
├── pyproject.toml              uv workspace root; ruff/mypy/pytest/import-linter
├── uv.lock                     Locked dependency tree
├── docker-compose.yml          PostgreSQL 16 + API + Web dev stack
└── .github/workflows/
    ├── ci.yml                  7 jobs on every PR
    └── nightly.yml             4 jobs (determinism, property, eval, e2e)
```

---

## 6. Completed Epics

### Epic 0 — Repository Foundation
**Commit:** `727352a`  
**Branch:** `main`

Full monorepo scaffold: uv workspace, FastAPI skeleton, React 18 + TypeScript + Vite, Docker Compose, GitHub Actions CI (7 jobs + 4 nightly), import-linter contracts, pre-commit hooks, frozen Pydantic v2 domain models, all 8 compute engine stubs and 4 reasoning module stubs, test suite scaffolding, documentation.

---

### Epic 1 — Database Foundation
**Commits:** `e11aa1f` (complete), `f0c0367` (validated)  
**Branch:** `main`

20 Alembic migrations (0001→0020) creating the complete PostgreSQL schema:

| Migration | Description |
|-----------|-------------|
| 0001 | Counterparties, positions (unpartitioned), collateral |
| 0002 | Reference data: risk weights, HQLA haircuts, run-off rates, CCFs, yield curves |
| 0003 | Snapshots |
| 0004 | Compute runs: audit record for every engine invocation |
| 0005 | Reasoning runs: audit trail for Claude invocations |
| 0006 | Audit log: append-only, hash-chained with DDL immutability trigger |
| 0007 | Workflow: workpapers, sign-offs, close calendar tasks |
| 0008 | Positions as range-partitioned table (by `reporting_date`); collateral composite FK |
| 0009 | Legal entities and entity-level capital requirements |
| 0010 | Product catalog: product groups, products, behavioural assumptions |
| 0011 | Cashflows and cashflow projections (range-partitioned by `cashflow_date`) |
| 0012 | Balance sheet line items and summaries |
| 0013 | LCR result tables (HQLA, inflow, outflow components) |
| 0014 | NSFR result tables (ASF and RSF components) |
| 0015 | Capital adequacy result table (CET1, Tier 1, Total Capital, RWA, ratios) |
| 0016 | Scenario management: scenario definitions and parameter sets |
| 0017 | Stress testing: runs, results, position-level impacts |
| 0018 | Structural Liquidity Statement (SLS / RBI DSB-II) |
| 0019 | Regulatory parameter history, filings, and filing lineage |
| 0020 | Demo seed data: 12 counterparties, 31 positions, 5 scenarios, reference data |

**Validation results:** Full downgrade-to-base → upgrade-to-head cycle confirmed. 65 tables, 96 FKs, 293 indexes. Audit log DDL trigger verified. Unit tests 13/13 pass.

---

### Epic 2A — FastAPI Platform Foundation
**Commits:** `44ba6cf` (complete), `ab672c7` (validated)  
**Branch:** `main`

FastAPI service wired to PostgreSQL via async SQLAlchemy 2.0. Health endpoints (`/health`, `/health/db`). Alembic integration. uv workspace syncing. Docker health check. 10/10 success criteria met.

**Bugs fixed during validation:** Docker health check path; SQL echo noise removed.

---

### Epic 2B — Domain API Layer
**Commits:** `22db6b8` (complete), `eec7ddb` (validated)  
**Branch:** `main`

9 domain modules fully implemented under `/v1/`:

| Domain | Routes | Notes |
|--------|--------|-------|
| Legal Entities | CRUD + list | `sort_by` allowlist enforced |
| Product Catalog | Groups + Products + BehavioralAssumptions | Two `sort_by` allowlists |
| Counterparties | CRUD + list | |
| Positions | CRUD + list + pagination | |
| Cashflows | CRUD + list | |
| Snapshots | CRUD + lifecycle (DRAFT→LOCKED→FILED) | |
| Scenarios | CRUD + list | |
| Stress Tests | CRUD + list | |
| Capital Requirements | CRUD + list | |

**Total:** 55 routes. **Validation:** 71/71 checks passed.

**Bugs fixed during validation:**
- `sort_by` silent fallback replaced with HTTP 400 across all 9 services (SQL injection prevention)
- `SnapshotUpdate` schema was missing `status` field — lifecycle guard was unreachable; fixed

---

### Epic 2C — Financial Calculation Engines
**Commit:** `217d1e0`  
**Branch:** `main`

9 deterministic financial engines implemented under `engines/`:

| Engine | Module | Formula Refs |
|--------|--------|--------------|
| LCR | `engines/liquidity/lcr.py` | BCBS LCR30.40, LCR30.42, LCR30.43, LCR40.73 |
| NSFR | `engines/liquidity/nsfr.py` | BCBS NSF10, NSF20, NSF30 |
| SLS | `engines/liquidity/sls.py` | RBI DSB-II, RBI Master Direction 2019 |
| Capital | `engines/capital/engine.py` | BCBS CRE20, CAP10, LEV10, RBI 2023 |
| Balance Sheet | `engines/balance_sheet/engine.py` | IFRS Conceptual Framework, RBI Format A |
| Cashflow | `engines/alm/cashflow.py` | RBI DSB-II, ALM standard |
| Liquidity Gap | `engines/alm/gap.py` | ALM maturity gap, RBI DSB-II |
| Scenario | `engines/stress/scenario.py` | Absolute / relative / replace shocks |
| Stress Test | `engines/stress/engine.py` | BCBS Stress principles 2018, RBI framework |

Shared infrastructure: `engines/common/utils.py` (`canonical_hash`, `quantize`, `safe_divide`), `engines/common/audit.py` (`EngineTrace`, `EngineResult[T]`), `engines/common/models.py` (all typed input models).

**Engineering properties:** All arithmetic uses `decimal.Decimal`. Pure functions — no DB calls inside engines. SHA-256 canonical hash on every inputs/outputs pair. `EngineTrace` with BCBS/RBI formula refs on every result. `VERSION = "1.0.0"` in every module.

**Unit tests:** 126/126 passing. Full validation report: `docs/engine_validation_report_epic2c.md`.

**Golden validation against BSM Demo Bank (2026-03-31):**

| Engine | Key Output | Value | Status |
|--------|-----------|-------|--------|
| LCR | Ratio (from components) | 26.41 | ✓ Passes (>1.0) |
| NSFR | Ratio | 1.2727 | ✓ Passes (>1.0) |
| Capital | CET1 ratio | 11.23% | ✓ Passes (>4.5%) |
| Capital | T1 ratio | 12.83% | ✓ Passes (>6.0%) |
| Capital | TCR | 16.05% | ✓ Passes (>8.0%) |
| Capital | Leverage | 8.32% | ✓ Passes (>3.0%) |
| Balance Sheet | Assets = Liab + Equity | 325,000 = 292,500 + 32,500 | ✓ Balanced |

---

### Epic 3 — React Frontend + Analytics API
**Commits:** `45bc40c` (complete), `6ba7e2f` (validated)  
**Branch:** `main`

React 18 + TypeScript SPA with Vite, Tailwind CSS, TanStack Query, Recharts. 7 pages implemented. Analytics read-only API added to backend.

**Pages implemented:**

| Page | Route | Data Source |
|------|-------|-------------|
| Login | `/login` | Placeholder auth (real auth Epic 5+) |
| Dashboard | `/` | `/v1/snapshots`, `/v1/scenarios`, `/v1/positions` |
| Position Browser | `/positions` | `/v1/positions` (paginated) |
| Scenario Browser | `/scenarios` | `/v1/scenarios` |
| LCR Dashboard | `/analytics/lcr` | `/v1/analytics/lcr` |
| NSFR Dashboard | `/analytics/nsfr` | `/v1/analytics/nsfr` |
| Balance Sheet | `/analytics/balance-sheet` | `/v1/analytics/balance-sheet`, `/v1/analytics/positions/summary` |

**Analytics API** (`apps/api/app/routers/analytics.py` — 5 read-only GET endpoints):
- `GET /v1/analytics/lcr` — reads `lcr_results`
- `GET /v1/analytics/nsfr` — reads `nsfr_results`
- `GET /v1/analytics/capital` — reads `capital_results`
- `GET /v1/analytics/balance-sheet` — reads `balance_sheet_summaries`
- `GET /v1/analytics/positions/summary` — aggregates `positions`

**Build validation:** TypeScript strict check — 0 errors. Vite production build — 0 warnings. Full validation report: `docs/frontend_validation_report_epic3.md`.

---

## 7. Current Git State

| Branch | Status | HEAD |
|--------|--------|------|
| `main` | Active — working tree clean | `1f4b8b2` (Epic 5 - Executive Intelligence Dashboard) |

**Commit log (13 epics, 17 commits):**

```
1f4b8b2 Epic 5 - Executive Intelligence Dashboard
1a4983a Epic 4D.1 - Integrate official SAM avatar
7c7c796 Epic 4D - Agentic AI Planner
ddac200 Update PROJECT_STATUS.md for Epics 4A–4C
f953e33 Epic 4C - AI Workflow and Report Automation
6ea1f6c Epic 4B - Banking Intelligence Layer
0d0648d Epic 4A - AI Copilot infrastructure
5be3e36 Epic 3.1 - Frontend stabilization
6ba7e2f Epic 3 - Frontend Validation Report
45bc40c Epic 3 - React frontend and analytics API
217d1e0 Epic 2C - Financial calculation engines
eec7ddb Epic 2B - Fix sort_by validation and snapshot status transition
22db6b8 Epic 2B - Domain API layer
ab672c7 Epic 2A - Fix Docker health check and SQL echo
44ba6cf Epic 2A - FastAPI platform foundation
f0c0367 Epic 1 - Database foundation validated
e11aa1f Epic 1 - Database foundation complete
727352a Epic 0 - Repository foundation
```

**Git tags:**
- `v0.1-database-foundation` — Epic 1
- `v0.3-frontend-stable` — Epic 3.1
- `v0.4-copilot-infrastructure` — Epic 4A
- `v0.4-banking-intelligence` — Epic 4B
- `v0.4-ai-workflow` — Epic 4C
- `v0.5-agentic-ai` — Epic 4D
- `v0.5.1-sam-avatar` — Epic 4D.1
- `v0.6-executive-dashboard` — Epic 5

---

## 8. Current Implementation Status

### Layer-by-layer completion

| Layer | Status | Notes |
|-------|--------|-------|
| **Database schema** | Complete | 65 tables, 20 migrations, validated |
| **Domain models** | Complete | Frozen Pydantic v2 models in `shared/domain` |
| **ORM models** | Complete | SQLAlchemy 2.0 models in `apps/api/app/db/models/` |
| **API — Domain layer** | Complete | 9 domains, 55 routes, all validated |
| **API — Analytics layer** | Complete | 5 read-only analytics endpoints |
| **Compute engines** | Complete | 9 engines, 126/126 unit tests pass |
| **Frontend screens** | Complete | 7 pages, TypeScript 0 errors |
| **Reasoning modules** | Complete | 7 reasoning modules (Epics 4A/4B/4C) |
| **Auth / OIDC** | Placeholder | Login always succeeds; real auth Epic 5+ |
| **Workflow** | Not started | DB tables exist; no business logic |
| **Audit log writer** | Not started | `shared/audit/` stub; DB trigger exists |
| **Observability** | Not started | OTel wired in dependencies only |
| **CI/CD** | Complete | 7 CI + 4 nightly jobs defined |
| **Docker** | Complete | Multi-stage builds; `uv.lock` committed |
| **Unit tests — engines** | 126/126 | All passing |
| **Unit tests — domain** | Passing | Domain model round-trip and constraints |

### Percentage complete

```
Foundation (Epics 0–1):     ████████████████████  2 / 2   100%
Core API + Engines (2A–2C): ████████████████████  3 / 3   100%
Frontend (Epic 3):          ████████████████████  1 / 1   100%
AI Copilot (Epics 4A–4C):   ████████████████████  3 / 3   100%
Auth + Workflow (Epics 5+): ░░░░░░░░░░░░░░░░░░░░  0 / ?     0%
Production hardening:       ░░░░░░░░░░░░░░░░░░░░  0 / 1     0%
────────────────────────────────────────────────────────────
Implemented layers (9):                           9 / ~13  ~70%
```

---

## 9. Known Limitations and Technical Debt

| Item | Severity | Location | Description |
|------|----------|----------|-------------|
| Analytics reads pre-seeded data | Medium | `apps/api/app/routers/analytics.py` | Analytics endpoints read stored result rows from seed data; engines are not wired to live computation. Results update only when the result tables are updated. |
| LCR seed data inconsistency | Low | `lcr_results` table | `total_outflows=110,000` in summary row does not match `lcr_outflow_components` sum of 20,800. Component data is self-consistent; the summary row appears to include committed facilities not in the component table. |
| Auth is a placeholder | High | `apps/web/src/context/AuthContext.tsx` | Login always succeeds; no JWT, no session. OIDC integration reserved for Epic 5+. |
| NSFR RSF rounding ±0.50 | Low | `nsfr_results` table | `loans_corporate_gt1y: 53,750 × 0.85 = 45,687.50` rounded to 45,688 in DB seed. Engine exact output is 197,999.50 vs seeded 198,000. Correct engine behaviour; documented in Engine Validation Report. |
| Port 5432 conflict (local dev) | Low | Docker Compose | Local PostgreSQL intercepts `localhost:5432`; Docker remaps to 5433. See `dev_environment.md` in memory. |
| `apps/workers` | Low | `apps/workers/` | Stub only; no worker framework integrated |
| COREP/FINREP | Deferred | `reports/regulatory/` | EU regulatory returns deferred to v2 |
| IRRBB, ECL, FTP engines | Not started | `engines/irrbb/`, `engines/ecl/`, `engines/ftp/` | Post-MVP engines; stubs only |
| OIDC integration | Pending | `apps/api/app/auth/` | Placeholder only; Epic 5+ |
| Object storage | Pending | `data/snapshot/` | Snapshot binaries in PostgreSQL; S3/GCS for production |

---

## 10. Completed: Epics 4A–4C — AI Copilot Layer

### Epic 4A — AI Copilot Infrastructure (`0d0648d`, tag: `v0.4-copilot-infrastructure`)
SSE streaming chat (`/v1/copilot/chat`), session CRUD, context builder (reads pre-computed LCR/NSFR/Capital/BalanceSheet from DB), AIProvider ABC + AnthropicProvider, migration 0022. Frontend: CopilotPage with session sidebar + streaming chat.

### Epic 4B — Banking Intelligence Layer (`6ea1f6c`, tag: `v0.4-banking-intelligence`)
7 reasoning modules (Liquidity, Capital, Balance Sheet, ALM, Stress, Regulatory, Executive), intent classifier, evidence citation system, 53 prompts across 8 domains. McKinsey/BCG system prompt persona. 118/118 tests.

### Epic 4C — AI Workflow and Report Automation (`f953e33`, tag: `v0.4-ai-workflow`)
15 AI workflow tools (ToolRegistry, ToolEvidence provenance), 10 Markdown-exportable report types with PDF/DOCX export_hints, conversation memory (SessionMemory, migration 0023), workflow executor (SSE, Anthropic tool_use API, mock fallback), 6 new API endpoints, Reports panel + Evidence panel frontend components. 85 new tests; 342/342 total pass.

## 11. Completed: Epic 4D — Agentic AI Planner (`7c7c796`, tag: `v0.5-agentic-ai`)

IntentAnalyzer, ExecutionPlan, PlanExecutor, ExecutionMonitor, ReasoningTimeline, AutonomousMonitor (LCR/NSFR/Capital thresholds), 6 agent API endpoints (`/v1/copilot/agent/`), 4-tab Copilot UI (Reports/Evidence/Plan/Alerts), AgentProfile. 115 new tests; 453/453 total pass.

### Epic 4D.1 — Official SAM Avatar (`1a4983a`, tag: `v0.5.1-sam-avatar`)

`SamAvatar` component (circular, 28–64px, white border, blue glow, hover animation), integrated across 9 Copilot surfaces. AgentProfile updated: SAM / Supervisory AI Manager / Senior Banking Intelligence Advisor / ● Online. 0 TS errors; 0 Vite warnings.

### Epic 5 — Executive Intelligence Dashboard (`1f4b8b2`, tag: `v0.6-executive-dashboard`)

New landing page replacing the Ops Dashboard. SAM as focal point. 9 dashboard components:
- `BankHealthIndicator` — Healthy/Warning/Critical derived from engine pass/fail flags
- `ExecutiveSAMPanel` — Avatar, dynamic greeting (health × entity × time-of-day), executive summary, CTA buttons
- `RegulatoryStatusGrid` — LCR, NSFR, CET1, Tier1, TCR, Leverage with Ask SAM buttons
- `InsightCard` — Liquidity, Capital, Funding, Stress with drivers + recommendation
- `RiskHeatmap` — 6-category Green/Amber/Red with hover explanations
- `TrendChart` — LCR/NSFR and CET1/Leverage line charts over last 5 snapshots
- `ExecutiveDashTimeline` — Event timeline (snapshot, engines, alerts, reports)
- `ExecutiveReports` — 7 executive report quick actions
- `AskSAMButton` — Context-aware Copilot navigation with sessionStorage prefill

Theme system: `ThemeContext` (dark/light, localStorage, TopBar toggle). All metrics consumed from existing APIs — no recalculation. 46/46 new tests. Validation report: `docs/epic5_validation_report.md`.

---

## 12. Remaining Roadmap to Production

| Phase | Scope | Status |
|-------|-------|--------|
| Epics 4A–4C | AI Copilot (infrastructure, intelligence, workflows) | Complete |
| Epic 4D | Pending approval | — |
| Epic 5 | Auth + OIDC (Okta / Azure AD, JWT, session management) | Not started |
| Epic 6 | Workflow (workpaper assembly, maker-checker sign-off) | Not started |
| Epic 7 | Engine wiring (live computation from API, not pre-seeded results) | Not started |
| Epic 8 | Additional engines (IRRBB, ECL, FTP) | Not started |
| Epic 9 | Frontend Phase 2 (workpaper view, regulatory wizard, conversational UI) | Not started |
| Phase 27 | Production hardening (pen test, DR drill, SLA validation, audit) | Not started |

**Phase 27 (Final productionisation)** per `build-pack/Phase27.md`:
- Reasoning layer boundary audit + eval harness (500+ cases, ≥95% pass rate)
- Historical reproduction test (12 months of filings, bit-identical)
- Security hardening (pen test, vault integration, TLS enforcement)
- Performance validation against SLAs (LCR ≤ 5 min, capital ≤ 30 min, Q&A ≤ 3s)
- Disaster recovery drill and runbooks

---

*This document is updated at the start and end of each Epic. For the authoritative feature specification, refer to `build-pack/Final_Build_Pack.md`. For architectural constraints, see `docs/ARCHITECTURE.md`. For development environment quirks, see the memory index at `.claude/projects/.../memory/MEMORY.md`.*
