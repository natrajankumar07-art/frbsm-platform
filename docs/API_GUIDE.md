# BSM Platform — API Reference Guide

> **Version:** v1.0-demo  
> **Base URL:** `http://localhost:8000`  
> **Auth:** Bearer token in `Authorization` header  
> **Format:** All requests/responses are JSON

---

## Authentication

### Login
```
POST /v1/auth/login
```
```json
{ "email": "demo@bsmplatform.in", "password": "demo" }
```
Response: `{ "access_token": "...", "token_type": "bearer" }`

---

## Entities

### List Legal Entities
```
GET /v1/entities
```
Returns all legal entities visible to the authenticated user.

### Get Entity
```
GET /v1/entities/{entity_id}
```

---

## Snapshots

### List Snapshots
```
GET /v1/snapshots?entity_id={id}&limit=10
```

### Create Snapshot
```
POST /v1/snapshots
```
```json
{ "entity_id": "uuid", "snapshot_date": "2025-12-31", "description": "Q4 2025" }
```

### Get Snapshot
```
GET /v1/snapshots/{snapshot_id}
```

---

## Analytics

### LCR Results
```
GET /v1/analytics/lcr?entity_id={id}&snapshot_id={id}
```
Returns:
```json
{
  "lcr_ratio": 1.287,
  "hqla_total": 45200000,
  "net_cash_outflows": 35120000,
  "hqla_level1": 38000000,
  "hqla_level2a": 5200000,
  "hqla_level2b": 2000000,
  "total_outflows": 42000000,
  "total_inflows": 6880000,
  "inflow_cap": 12600000
}
```

### NSFR Results
```
GET /v1/analytics/nsfr?entity_id={id}&snapshot_id={id}
```
Returns: `{ "nsfr_ratio", "asf_total", "rsf_total", "asf_breakdown": {...}, "rsf_breakdown": {...} }`

### Capital Results
```
GET /v1/analytics/capital?entity_id={id}&snapshot_id={id}
```
Returns: `{ "cet1_ratio", "tier1_ratio", "total_capital_ratio", "leverage_ratio", "rwa_total", "cet1_capital" }`

### Balance Sheet
```
GET /v1/analytics/balance-sheet?entity_id={id}&snapshot_id={id}
```
Returns: `{ "total_assets", "total_liabilities", "total_equity", "asset_breakdown": {...} }`

---

## Positions

### List Positions
```
GET /v1/positions?entity_id={id}&snapshot_id={id}&limit=100
```

### Create Position
```
POST /v1/positions
```
```json
{
  "entity_id": "uuid",
  "snapshot_id": "uuid",
  "product_type": "HQLA_L1",
  "counterparty_id": "uuid",
  "notional": 5000000,
  "currency": "USD",
  "maturity_date": "2026-03-31"
}
```

---

## AI Copilot

### Create Session
```
POST /v1/copilot/sessions
```
```json
{ "entity_id": "uuid" }
```

### Send Message
```
POST /v1/copilot/sessions/{session_id}/messages
```
```json
{
  "content": "What is our current LCR position?",
  "context": { "metric": "LCR", "snapshot_id": "uuid" }
}
```
Response includes SAM's reply and the tool call timeline.

### Get Session History
```
GET /v1/copilot/sessions/{session_id}/messages
```

---

## Autonomous Intelligence

### Alerts

#### List Alerts
```
GET /v1/autonomous/alerts?status=open&entity_id={id}&limit=20
```
Status: `open` | `acknowledged` | `resolved`

#### Acknowledge Alert
```
PATCH /v1/autonomous/alerts/{alert_id}
```
```json
{ "status": "acknowledged" }
```

### Recommendations

#### List Recommendations
```
GET /v1/autonomous/recommendations?status=active&limit=10
```

#### Update Recommendation
```
PATCH /v1/autonomous/recommendations/{rec_id}
```
```json
{ "status": "implemented" }
```
Status: `active` | `implemented` | `dismissed`

### Briefings

#### List Briefings
```
GET /v1/autonomous/briefings?entity_id={id}&type=morning&limit=10
```
Types: `morning` | `daily_summary` | `weekly_summary` | `monthly_board` | `quarterly_executive`

#### Generate Briefing
```
POST /v1/autonomous/briefings/generate
```
```json
{ "entity_id": "uuid", "briefing_type": "morning" }
```
Calls Claude to generate the briefing and persists it. May take 3–8 seconds.

### Issues

#### List Issues
```
GET /v1/autonomous/issues?status=open&entity_id={id}
```

#### Create Issue
```
POST /v1/autonomous/issues
```
```json
{
  "entity_id": "uuid",
  "title": "LCR buffer at minimum",
  "description": "...",
  "category": "liquidity",
  "severity": "warning"
}
```

#### Update Issue Status
```
PATCH /v1/autonomous/issues/{issue_id}
```
```json
{ "status": "monitoring" }
```
Status: `open` | `monitoring` | `resolved`

### Scheduled Reports

#### List Schedules
```
GET /v1/autonomous/scheduled-reports?entity_id={id}
```

#### Create Schedule
```
POST /v1/autonomous/scheduled-reports
```
```json
{
  "entity_id": "uuid",
  "report_type": "cro_report",
  "frequency": "weekly"
}
```

#### Toggle Schedule
```
PATCH /v1/autonomous/scheduled-reports/{schedule_id}
```
```json
{ "is_active": false }
```

#### Delete Schedule
```
DELETE /v1/autonomous/scheduled-reports/{schedule_id}
```

### Monitoring

#### Get Scheduler Status
```
GET /v1/autonomous/status
```
Returns: `{ "interval_seconds": 900, "next_run_at": "...", "last_run_at": "..." }`

#### Trigger Manual Run
```
POST /v1/autonomous/monitor/run
```
Runs the full monitoring cycle immediately and returns the run record.

### Activity Feed
```
GET /v1/autonomous/activity?entity_id={id}&limit=20
```
Returns merged timeline of alerts, briefings, and monitoring runs.

---

## Workflows

### List Workflows
```
GET /v1/workflows?entity_id={id}
```

### Create Workflow
```
POST /v1/workflows
```

### Get Workflow
```
GET /v1/workflows/{workflow_id}
```

---

## Reports

### Generate Report
```
POST /v1/reports/generate
```
```json
{
  "entity_id": "uuid",
  "report_type": "ceo_summary",
  "snapshot_id": "uuid"
}
```
Report types: `ceo_summary` | `cro_report` | `board_pack` | `icaap` | `ilaap` | `liquidity_summary` | `capital_summary`

---

## Health

### Health Check
```
GET /healthz
```
Returns: `{ "status": "ok", "db": "ok", "version": "1.0.0" }`

---

## Error Responses

All errors follow:
```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE"
}
```

Common HTTP status codes:
| Code | Meaning |
|------|---------|
| 400 | Invalid request body |
| 401 | Missing or invalid token |
| 404 | Resource not found |
| 422 | Validation error (Pydantic) |
| 500 | Internal server error |

---

## Interactive Docs

When `APP_MODE=local`, interactive API docs are available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
