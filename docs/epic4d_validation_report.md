# Epic 4D Validation Report — Agentic AI Planner (SAM)

**Date:** 2026-07-01  
**Branch:** main  
**Prior commit:** `ddac200` (PROJECT_STATUS.md update for Epics 4A–4C)

---

## 1. Summary

Epic 4D transforms the FRBSM AI Copilot into an agentic banking intelligence system. The agent is internally named **SAM (Supervisory AI Manager)**. SAM can understand complex requests, create execution plans, select and run tools, monitor execution, build reasoning timelines, and perform autonomous threshold monitoring — all while remaining fully auditable and never computing financial ratios.

**All 453 unit tests pass. Zero regressions.**

---

## 2. Architecture

### Layer Architecture

```
User Request
     ↓
Intent Analysis          (intent_analyzer.py — keyword/pattern scoring)
     ↓
Planner                  (planner/base.py + tool_selector.py)
     ↓
Tool Selection           (tool_selector.py — builds ExecutionStep list)
     ↓
Workflow Executor        (planner/executor.py — SSE streaming, retry, deps)
     ↓
Memory                   (memory.py — resolve_reference() for conversation refs)
     ↓
Reasoning Timeline       (reasoning_timeline.py — 7-stage explainability)
     ↓
Report Generator         (reports/generators.py — unchanged from 4C)
     ↓
Final Response (SSE stream)
```

### Architectural Boundaries (maintained)

| Constraint | Status |
|---|---|
| SAM never computes LCR / NSFR / Capital / Balance Sheet | PASS |
| SAM only consumes pre-computed engine outputs from DB | PASS |
| No modification to financial engines | PASS |
| No modification to Epic 4A/4B/4C infrastructure | PASS |
| Tool registry (15 tools) unchanged | PASS |
| Reasoning layer (7 modules) unchanged | PASS |

---

## 3. New Backend Components

### 3.1 Planner Package (`apps/api/app/services/ai/planner/`)

| File | Contents |
|---|---|
| `base.py` | `StepStatus`, `PlanStatus`, `TimelineStage`, `TimelineEvent`, `ExecutionStep`, `ExecutionPlan` |
| `intent_analyzer.py` | `IntentAnalysis` dataclass, `analyze_intent()` — keyword scoring for 6 intents × 8 domains |
| `tool_selector.py` | `select_tools()` — converts IntentAnalysis → ordered ExecutionStep list with deps |
| `executor.py` | `PlanExecutor` — async SSE generator, dependency ordering, retry, state tracking |
| `__init__.py` | Package exports |

**ExecutionPlan** decomposes any user request into ordered steps:
- Each `ExecutionStep` tracks: tool_name, params, depends_on, status, start/end times, duration_ms, retry_count, evidence
- Dependency resolution ensures steps run in correct order
- Failed deps cause downstream steps to be skipped (not crashed)

**IntentAnalysis** detects:
- Primary intent: list, compare, analyze, generate_report, monitor, stress, summarize, explain
- Domain: lcr, nsfr, capital, balance_sheet, alm, stress, regulatory, executive
- Conversational references: "same entity", "last month", "generate another report", "repeat"
- Date mentions extracted via regex
- Confidence score 0.5–0.95

### 3.2 Execution Monitor (`apps/api/app/services/ai/execution_monitor.py`)

`ExecutionMonitor` — in-memory ring buffer (50 records max):
- Records per execution: execution_id, plan_id, intent, entity_id, snapshot_id, status
- Records per step: tool_name, description, status, start/end time, duration_ms, retry_count, evidence_confidence
- `record_from_plan(plan)` converts completed `ExecutionPlan` to `ExecutionRecord`
- Module-level singleton `get_monitor()` shared across all requests

### 3.3 Reasoning Timeline (`apps/api/app/services/ai/reasoning_timeline.py`)

`build_timeline(plan)` produces a 7-stage `TimelineEvent` list:

1. **Intent Analysis** — truncated user intent (≤120 chars)
2. **Execution Planning** — step count + domains detected
3. **Tool Execution** — tool names list (≤4 shown), failure count
4. **Evidence Collection** — source count + HIGH confidence count
5. **Reasoning** — "Applied banking intelligence to synthesize findings" (generic — no chain-of-thought)
6. **Report Generation** — only shown when report tools ran
7. **Final Answer** — completion summary or failure message

Rules: no chain-of-thought, no internal parameters, no tool input/output values exposed.

### 3.4 Autonomous Monitor (`apps/api/app/services/ai/autonomous_monitor.py`)

Background monitoring checks (reads from DB result tables, never modifies data):

| Check | Breach Threshold | Warning Threshold | Severity |
|---|---|---|---|
| LCR | < 100% | < 110% | CRITICAL / HIGH |
| NSFR | < 100% | < 105% | CRITICAL / MEDIUM |
| CET1 | < 4.5% | < 6.0% | CRITICAL / HIGH |
| Tier 1 | < 6.0% | < 8.0% | CRITICAL / HIGH |
| Total Capital | < 8.0% | < 10.0% | CRITICAL / HIGH |
| Leverage | < 3.0% | < 4.0% | CRITICAL / HIGH |

Generates `Alert` objects: alert_id, severity, category, title, message, entity, snapshot_date, metric_name, metric_value, threshold.

### 3.5 Conversation Intelligence (`memory.py` — additive only)

Added `SessionMemory.resolve_reference()`:

| Reference | Resolved To |
|---|---|
| `"active_entity"` | entity_id + entity_name from session |
| `"active_snapshot"` | snapshot_id + snapshot_date from session |
| `"previous_month"` | second-most-recent snapshot_id |
| `"previous_quarter"` | second-most-recent snapshot_id |
| `"repeat_analysis"` | last tool_name + summary from tool call history |
| `"repeat_report"` | last report_type from report history |

### 3.6 API Router (`apps/api/app/routers/agent.py`)

6 new endpoints under `/v1/copilot/agent/`:

| Method | Path | Description |
|---|---|---|
| POST | `/chat` | Full SAM agentic chat (SSE): intent → plan → execute → timeline |
| POST | `/plan` | Create execution plan without running (dry-run, JSON) |
| GET | `/history` | Get execution history (most-recent-first) |
| GET | `/alerts` | Run autonomous monitoring checks, return structured alerts |
| GET | `/timeline/{plan_id}` | Retrieve reasoning timeline for a past execution |
| POST | `/analyze-intent` | Analyze intent of a message without executing tools |

---

## 4. New Frontend Components

| File | Description |
|---|---|
| `AgentProfile.tsx` | SAM identity placeholder — name, title, avatar (S), status dot. Epic 5 provides final avatar without changing props. |
| `ExecutionTimeline.tsx` | 7-stage vertical timeline with status icons, timestamps, detail text |
| `PlannerPanel.tsx` | Live execution plan view — step list, status badges, progress bar, durations |
| `AlertPanel.tsx` | Regulatory alert panel with severity colours (red/orange/yellow/blue), metric values |
| `CopilotPage.tsx` | Enhanced: SAM profile in header, 4-tab right panel (Reports/Evidence/Plan/Alerts), `agentStatus` state |

### Right Panel Tabs

| Tab | Icon | Content |
|---|---|---|
| Reports | FileText | ReportPanel (10 report types, from 4C) |
| Evidence | ShieldCheck | EvidencePanel (provenance, from 4C) |
| Plan | LayoutList | ExecutionTimeline + PlannerPanel |
| Alerts | Bell | AlertPanel (autonomous monitoring) |

**TypeScript:** zero errors (`npm run typecheck` clean).

---

## 5. SAM Identity (Placeholder)

`AgentProfile` component registered with:
- Name: "SAM"
- Title: "Supervisory AI Manager"
- Description: "Intelligent banking teammate — explains regulatory position using validated engine outputs."
- Status: idle | active | thinking | error
- Avatar: "S" placeholder — Epic 5 introduces final avatar by passing an `avatarUrl` prop (no backend changes needed)

---

## 6. Workflow Examples

### Example 1 — "Analyze LCR for Demo Bank"

```
Intent:  analyze (confidence: 0.80) | domains: lcr
Plan:    [list_entities → get_snapshots → summarize_regulatory_results]
Events:  plan_start, step_complete ×3, plan_complete, timeline_ready, agent_done
```

### Example 2 — "Compare with last month" (conversation reference)

```
Memory:  active_entity=BSM Demo Bank, recent_snapshots=[snap-Apr, snap-Mar]
Resolved: snapshot_reference=previous_month → snap-Mar
Intent:  compare
Plan:    [list_entities → get_snapshots → compare_snapshots]
```

### Example 3 — "Generate board pack" (report intent)

```
Intent:  generate_report | report_type_hint=board_pack
Plan:    [list_entities → get_snapshots → generate_executive_summary (report_type=board_pack)]
```

### Example 4 — Autonomous monitoring alert

```
GET /v1/copilot/agent/alerts
→ Queries lcr_results, nsfr_results, capital_results
→ Any ratio below threshold → CRITICAL alert
→ All thresholds met → empty alerts list
```

---

## 7. Test Results

### 7.1 Epic 4D — New Tests

| File | Tests | Status |
|---|---|---|
| `test_planner.py` | 37 | PASS |
| `test_tool_selector.py` | 19 | PASS |
| `test_execution_monitor.py` | 15 | PASS |
| `test_reasoning_timeline.py` | 13 | PASS |
| `test_autonomous_monitor.py` | 16 | PASS |
| `test_memory_references.py` | 15 | PASS |
| **4D Subtotal** | **115** | **PASS** |

### 7.2 Regression — All Prior Tests

| Suite | Tests | Status |
|---|---|---|
| Epic 4C (tool registry, reports, memory) | 85 | PASS |
| Epic 4A/4B (reasoning, evidence, prompts) | 118 | PASS |
| Engine tests (LCR, NSFR, Capital, BS, Stress, ALM) | 126 | PASS |
| Shared domain model tests | 13 | PASS  |
| **Total** | **453** | **PASS** |

---

## 8. Architecture Constraint Verification

```
┌──────────────────────────────────────────────────────────────┐
│  SAM IDENTITY LAYER (Epic 4D — NEW)                         │
│  AgentProfile placeholder — Epic 5 adds final avatar        │
├──────────────────────────────────────────────────────────────┤
│  PLANNER LAYER (Epic 4D — NEW)                              │
│  IntentAnalysis → ExecutionPlan → PlanExecutor              │
│  ReasoningTimeline (7 stages, no chain-of-thought)          │
│  ExecutionMonitor (50-record in-memory history)             │
│  AutonomousMonitor (LCR/NSFR/Capital threshold alerts)      │
├──────────────────────────────────────────────────────────────┤
│  TOOL LAYER (Epic 4C — UNCHANGED)                           │
│  15 tools, ToolRegistry, ToolEvidence                       │
│  Session memory + resolve_reference() (additive)            │
├──────────────────────────────────────────────────────────────┤
│  REASONING LAYER (Epic 4B — UNCHANGED)                      │
│  7 modules, intent classifier, evidence citations           │
├──────────────────────────────────────────────────────────────┤
│  AI INFRA (Epic 4A — UNCHANGED)                             │
│  AnthropicProvider, orchestrator, SSE chat, sessions        │
├──────────────────────────────────────────────────────────────┤
│  COMPUTE LAYER (Epics 1–2 — NEVER MODIFIED)                 │
│  LCR / NSFR / Capital / Balance Sheet / Stress engines      │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Known Limitations

| Item | Notes |
|---|---|
| Execution history is in-memory | Resets on API restart; DB persistence is a future enhancement |
| Autonomous monitoring runs on-demand | No background scheduler yet; `GET /alerts` triggers checks on each call |
| Intent analysis is keyword-based | No LLM call for intent — fast but may misclassify rare phrasings |
| `AgentProfile` avatar is a placeholder | Epic 5 provides final SAM visual identity |
| Tool executor max_retries=1 | Configurable; higher retry counts for flaky DB connections in production |

---

*Generated by FRBSM AI Copilot development pipeline.*
