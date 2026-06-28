# Frontend Validation Report — Epic 3
**Date:** 2026-06-28  
**Stack:** Vite 5 + React 18 + TypeScript 5.5 + Tailwind 3 + React Query 5 + Recharts 2 + React Router 6  
**Backend:** FastAPI 2026.1.0 on port 8000  
**Frontend:** Vite dev server on port 3000

---

## 1. Build & Type Check

| Check | Result |
|-------|--------|
| TypeScript strict type check (`tsc --noEmit`) | **PASS — 0 errors** |
| Vite production build (`npm run build`) | **PASS — 7 chunks, 0 warnings** |
| Bundle sizes (gzip) | react 0.09 kB, query 10.6 kB, router 53.5 kB, app 32.4 kB, charts 108 kB |

---

## 2. Application Startup

| Check | Result |
|-------|--------|
| Frontend dev server starts (`npm run dev`) | **PASS** — listening on port 3000 |
| HTML served at `http://localhost:3000/` | **PASS** — 200 OK |
| Vite `/api` proxy to FastAPI on port 8000 | **PASS** |

---

## 3. API Communication

Verified via `curl` through the Vite proxy:

| Endpoint | Status | Data |
|----------|--------|------|
| `GET /api/v1/legal-entities` | 200 | 4 entities returned |
| `GET /api/v1/positions` | 200 | 31 positions, paginated |
| `GET /api/v1/snapshots` | 200 | 4 snapshots |
| `GET /api/v1/scenarios` | 200 | Scenarios loaded |
| `GET /api/v1/analytics/lcr` | 200 | LCR ratio 1.5787 (PASS) |
| `GET /api/v1/analytics/nsfr` | 200 | NSFR ratio 1.2727 (PASS) |
| `GET /api/v1/analytics/capital` | 200 | CET1 ratio 0.1123 (PASS) |
| `GET /api/v1/analytics/balance-sheet` | 200 | Assets 325,000, Equity 32,500 |
| `GET /api/v1/analytics/positions/summary` | 200 | 31 positions by class |

---

## 4. Dashboard Data Verification

**Entity used:** BSM Demo Bank Ltd (`a1000000-0000-0000-0000-000000000001`)  
**Snapshot:** 2026-03-31 (`d1000000-0000-0000-0000-000000000001`, status: locked)

| Metric | API Value | Expected | Match |
|--------|-----------|----------|-------|
| LCR ratio | 1.5787 (157.87%) | >100% | ✓ PASS |
| NSFR ratio | 1.2727 (127.27%) | >100% | ✓ PASS |
| CET1 ratio | 11.23% | >4.5% | ✓ PASS |
| T1 ratio | 12.83% | >6.0% | ✓ PASS |
| Total Capital ratio | 16.05% | >8.0% | ✓ PASS |
| Leverage ratio | 8.32% | >3.0% | ✓ PASS |
| Balance Sheet | Assets 325,000 = Liab 292,500 + Equity 32,500 | Balanced | ✓ |
| Position count | 31 active | seeded count | ✓ |

---

## 5. Pages Implemented

| Page | Route | Data Source | Status |
|------|-------|-------------|--------|
| Login | `/login` | Mock auth (placeholder) | ✓ |
| Dashboard | `/` | `/v1/snapshots`, `/v1/scenarios`, `/v1/positions` | ✓ |
| Position Browser | `/positions` | `/v1/positions` (paginated) | ✓ |
| Scenario Browser | `/scenarios` | `/v1/scenarios` | ✓ |
| LCR Dashboard | `/analytics/lcr` | `/v1/analytics/lcr` | ✓ |
| NSFR Dashboard | `/analytics/nsfr` | `/v1/analytics/nsfr` | ✓ |
| Balance Sheet | `/analytics/balance-sheet` | `/v1/analytics/balance-sheet`, `/v1/analytics/positions/summary` | ✓ |

---

## 6. Architecture Compliance

| Requirement | Verified |
|-------------|---------|
| No business logic in frontend | ✓ All calculations in backend engines |
| Frontend only renders and calls APIs | ✓ |
| All calculations remain in backend | ✓ `/v1/analytics/*` reads stored results from DB |
| LCR/NSFR/Capital ratios from backend | ✓ Displayed as returned, no recomputation |
| No AI integration implemented | ✓ (reserved for Epic 4) |

---

## 7. Backend Addition

New read-only analytics router: `apps/api/app/routers/analytics.py`  
5 endpoints, all GET, all reading from stored result tables:
- `GET /v1/analytics/lcr` — reads `lcr_results`
- `GET /v1/analytics/nsfr` — reads `nsfr_results`
- `GET /v1/analytics/capital` — reads `capital_results`
- `GET /v1/analytics/balance-sheet` — reads `balance_sheet_summaries`
- `GET /v1/analytics/positions/summary` — aggregates `positions` table

---

## 8. Known Limitations

1. **Entity auto-selection**: The entity context auto-selects the first entity alphabetically. The seeded Demo Bank is 3rd in the list. User must switch entity via the top-bar dropdown to see analytics data. A future improvement would be to default to entities where `is_reporting_entity = true`.

2. **LCR seeded inconsistency**: The stored LCR ratio is 1.5787 (NCO=82,600) from the top-level `lcr_results` table. Component-level data computes NCO=5,200 → ratio=26.4. This seed data inconsistency is documented in the Engine Validation Report (Epic 2C).

3. **Auth is placeholder**: Login always succeeds with any email/password. Real auth (JWT or session) reserved for a future epic.

4. **Snapshot selector defaults**: Analytics pages auto-select the first snapshot (by list order). Locked snapshot `2026-03-31` appears first and has data.
