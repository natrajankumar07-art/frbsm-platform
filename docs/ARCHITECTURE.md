# BSM Platform — Architecture

> **Version:** v1.0-demo  
> **Audience:** Architects, Engineering Managers, Technical Due Diligence

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        BSM PLATFORM                              │
│                                                                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │   React 18  │   │   FastAPI   │   │    PostgreSQL 16     │   │
│  │  TypeScript │◄──►│   Python   │◄──►│    (async ORM)      │   │
│  │    Vite     │   │  Structlog  │   │    Alembic mig.     │   │
│  └─────────────┘   └──────┬──────┘   └─────────────────────┘   │
│                            │                                       │
│              ┌─────────────┼─────────────┐                       │
│              │             │             │                         │
│     ┌────────▼──┐  ┌───────▼────┐ ┌─────▼──────┐               │
│     │  Financial│  │  AI Layer  │ │  Workflow   │               │
│     │  Engines  │  │  (Claude)  │ │  Engine     │               │
│     │  (Python) │  │  15 Tools  │ │  (Planner)  │               │
│     └───────────┘  └────────────┘ └────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Three-Layer Architecture

The defining architectural principle of BSM Platform is the **strict separation** between financial computation and AI reasoning.

### Layer 1 — Compute Layer

**Location:** `shared/engines/`, `apps/api/app/services/engines/`

Python financial engines compute all regulatory ratios from position data. This layer has:
- No AI imports
- No Anthropic SDK
- No LLM calls
- Deterministic, reproducible results

**Engines:**
| Engine | Output |
|--------|--------|
| `lcr_engine.py` | LCR ratio, HQLA tiers, cash flows |
| `nsfr_engine.py` | NSFR ratio, ASF/RSF breakdown |
| `capital_engine.py` | CET1, Tier 1, TCR, Leverage |
| `balance_sheet_engine.py` | Total assets, liabilities, equity |
| `stress_test_engine.py` | Stressed ratios under scenarios |

All engine outputs are persisted to PostgreSQL and become the single source of truth for all downstream analytics.

### Layer 2 — Tool Layer

**Location:** `apps/api/app/services/ai/tools/`

15 structured tools bridge engine outputs to the AI reasoning layer. Each tool:
- Has a typed input schema
- Reads engine-stored results from the database
- Returns structured JSON
- Logs all inputs/outputs for audit

**Tool categories:**
- Analytics tools: `lcr_analysis`, `nsfr_analysis`, `capital_analysis`, `balance_sheet_analysis`, `positions_summary`
- Monitoring tools: `check_alerts`, `run_monitoring_checks`
- Reporting tools: `generate_report`
- Planning tools: `plan_task`, `execute_plan_step`

### Layer 3 — Reasoning Layer

**Location:** `apps/api/app/services/ai/`

Claude AI (via Anthropic SDK) reads tool outputs and generates:
- Executive summaries and briefings
- Risk analysis and explanations
- Recommendations and remediation guidance
- Regulatory question answers
- Report content

The reasoning layer has no direct access to the database — it only sees what tools return.

---

## Import Boundaries

Enforced by `import-linter` in CI. Violations fail the build.

| Rule | Source | Forbidden Target |
|------|--------|-----------------|
| Reasoning cannot import engines | `reasoning/*` | `engines/*` |
| Reasoning cannot use numpy/pandas | `reasoning/*` | `numpy`, `pandas` |
| Engines cannot import reasoning | `engines/*` | `reasoning/*` |
| Engines cannot use Anthropic SDK | `engines/*` | `anthropic` |
| API layer cannot bypass engines | `app.api.*` | `engines.*` direct |

---

## Data Flow

```
Position Data → Snapshot → Engine Computation → Database Storage
                                                        │
                              Tool Layer reads ─────────┘
                                    │
                              Claude receives tool outputs
                                    │
                              Claude generates insight
                                    │
                              Response to user
```

### Determinism Guarantee

Same snapshot + same engine version → bit-identical outputs.

- All engine inputs are SHA-256 hashed before the run.
- All engine outputs are SHA-256 hashed and stored in `ComputeRun`.
- Golden tests verify hash stability across code changes.

---

## Frontend Architecture

```
App.tsx (React Router v6)
├── Landing Page (pre-auth, /welcome)
├── Login Page (/login)
└── AppShell (requires auth)
    ├── Sidebar (navigation)
    ├── TopBar (entity selector, theme)
    ├── ProductTour (first-launch overlay)
    └── Routes (lazy-loaded via React.lazy + Suspense)
        ├── ExecutiveDashboard (/)
        ├── Analytics (/analytics/*)
        ├── Positions (/positions)
        ├── Copilot (/copilot)
        ├── Autonomous (/autonomous/*)
        ├── About SAM (/about-sam)
        └── Help (/help)
```

**State Management:**
- TanStack Query — server state (API data, caching, refetching)
- React Context — auth, entity selection, theme, product tour
- Local component state — UI state (modals, forms, selections)
- localStorage — theme preference, tour completion

**Code Splitting:**
Vite manual chunks split the bundle into: `react`, `router`, `query`, `charts`. All page routes (except LandingPage and Login) are lazy-loaded for optimal performance.

---

## API Architecture

**Deployment:** Modular monolith — single FastAPI service with all engines imported as Python packages.

```
apps/api/
├── app/
│   ├── main.py          # FastAPI app factory, lifespan
│   ├── routers/         # 14 router modules
│   ├── services/
│   │   ├── ai/          # SAM, tools, autonomous
│   │   ├── engines/     # Engine execution wrappers
│   │   └── workflow/    # Workflow orchestration
│   ├── db/
│   │   ├── models/      # SQLAlchemy ORM models
│   │   └── session.py   # Async session factory
│   ├── schemas/         # Pydantic v2 request/response
│   ├── repositories/    # Data access layer
│   └── config.py        # Pydantic settings
└── alembic/
    └── versions/        # 24 migrations (0001–0024)
```

---

## Database Schema

24 migrations define the complete schema. Key domains:

| Domain | Tables |
|--------|--------|
| Core | legal_entities, product_groups, products, counterparties |
| Positions | positions, cashflows |
| Snapshots | snapshots, snapshot_positions |
| Analytics | lcr_results, nsfr_results, capital_results, balance_sheet_results |
| Scenarios | scenarios, scenario_positions |
| Stress Tests | stress_tests, stress_test_results |
| Workflow | workflows, workflow_steps, workflow_events |
| AI | copilot_sessions, agent_executions, agent_tool_calls |
| Planner | planner_tasks, planner_steps |
| Autonomous | autonomous_alerts, autonomous_recommendations, autonomous_issues, autonomous_briefings, scheduled_report_configs, autonomous_monitoring_runs |

**Audit Log:** Append-only PostgreSQL table with a DDL trigger that rejects UPDATE and DELETE at the database level. Entries are SHA-256 hash-chained (each entry stores the hash of the previous entry).

---

## Autonomous Monitoring Architecture

```
FastAPI Lifespan
└── asyncio.create_task(run_scheduler())
    └── Infinite loop (every 900 seconds)
        ├── _run_monitoring()
        │   └── async_session_factory
        │       ├── run_monitoring_checks()
        │       ├── Persist new alerts (deduplication)
        │       ├── generate_recommendations()
        │       └── Persist new recommendations
        └── _run_morning_briefings() [if 06:00–06:14 UTC]
            └── For each reporting entity:
                ├── _fetch_latest_metrics()
                ├── generate_briefing()
                └── AutonomousBriefingModel.save()
```

---

## Security Model

1. **Compute/AI isolation** — Financial engines run with no Anthropic API access.
2. **Read-only AI access** — Claude receives only tool return values; it cannot write to the database directly.
3. **Tool sandboxing** — Each tool has a defined input/output schema. Tools cannot execute arbitrary SQL.
4. **Auth** — Current demo uses session-based auth. Production target: JWT with RBAC.
5. **Network** — API behind reverse proxy. PostgreSQL not publicly exposed.

---

## Epics Delivered

| Epic | Version | Description |
|------|---------|-------------|
| 0 | v0.0 | Repository setup and base infrastructure |
| 1 | v0.1 | Core data models and position management |
| 2A | v0.2 | LCR engine and analytics |
| 2B | v0.2 | NSFR engine and analytics |
| 2C | v0.2 | Capital engine and analytics |
| 3 | v0.3 | AI Copilot with tool-use |
| 3.1 | v0.3 | Workflow engine and report automation |
| 4A | v0.4 | Banking intelligence layer |
| 4B | v0.4 | Extended analytics and SAM identity |
| 4C | v0.4 | Workflow automation and report generation |
| 4D | v0.5 | Agentic AI planner |
| 4D.1 | v0.5 | Official SAM avatar |
| 5 | v0.6 | Executive Intelligence Dashboard |
| 6 | v0.7 | Autonomous Banking Intelligence |
| 7 | v1.0 | Demo and Production Readiness |
