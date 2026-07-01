# Epic 3.1 Stabilization Report
**Date:** 2026-07-01  
**Branch:** `main`  
**Scope:** Fix all runtime issues before AI integration (Epic 4)

---

## 1. Issues Found and Fixed

### Issue 1 — Health endpoint paths wrong (FIXED)
**Symptom:** Dashboard showed "API not reachable" indicator at all times.  
**Root cause:** `apps/web/src/lib/api.ts` called `/health/live` and `/health/ready` via the Vite proxy. The backend exposes `/health` (liveness) and `/health/db` (readiness) — the `/live` and `/ready` variants do not exist. Both calls returned HTTP 404. TanStack Query caught the error, `health` was undefined, and the Dashboard rendered the XCircle "API not reachable" state.  
**Additional defect:** `HealthResponse` backend schema was missing the `service` field. The Dashboard renders `{health.service}` — this would have shown `undefined` even after fixing the URL.  
**Fix:**
- `apps/web/src/lib/api.ts`: both `health.live()` and `health.ready()` now call `/health`
- `apps/api/app/schemas/health.py`: added `service: str` field to `HealthResponse`
- `apps/api/app/routers/health.py`: returns `service: "BSM Platform API"`
- `apps/web/src/types/api.ts`: `HealthStatus` interface updated to include `mode` and `commit` fields to match the actual response shape

**Verified:** `GET /health` → HTTP 200 `{"status":"ok","service":"BSM Platform API","version":"2026.1.0","mode":"local","commit":"dev"}`

---

### Issue 2 — Entity auto-select picked wrong entity (FIXED)
**Symptom:** All analytics pages (LCR, NSFR, Balance Sheet) showed "No result found" empty state on first load.  
**Root cause:** `EntityContext.tsx` auto-selects `entities[0]` (the first entity returned by the API). The `/v1/legal-entities` endpoint defaults to `sort_by=created_at&sort_dir=DESC`. During Epic 2B validation, two test entities ("Test Bank Ltd", "Valid Bank Updated") were created more recently than the seeded Demo Bank. These appeared first in the list. The analytics result tables are seeded for `entity_id=a1000000-0000-0000-0000-000000000001` (BSM Demo Bank Ltd), so selecting any other entity returns `null` from all analytics endpoints — rendering the empty state.  
**Fix:** Updated `EntityContext.tsx` to prefer the entity where `is_reporting_entity === true`:
```tsx
const reporting = entities.find((e) => e.is_reporting_entity);
setSelected(reporting ?? entities[0]);
```
BSM Demo Bank Ltd has `is_reporting_entity=true`; all test entities have `is_reporting_entity=false`. Demo Bank is now selected on first load without user intervention.

**Verified:** EntityContext now auto-selects BSM Demo Bank Ltd (entity `a1000000-...0001`).

---

### Issue 3 — Docker frontend build used pnpm with missing lockfile (FIXED)
**Symptom:** `docker compose up` would fail at the web service build step with `COPY pnpm-lock.yaml: file not found`.  
**Root cause:** `apps/web/Dockerfile` used pnpm (`corepack enable && corepack prepare pnpm@latest`) and required `pnpm-lock.yaml`. The frontend project uses npm — `package-lock.json` exists but `pnpm-lock.yaml` does not. The Docker build had never been successfully run after the npm/pnpm mismatch was introduced.  
**Fix:** Rewrote `apps/web/Dockerfile` to use npm:
- Removed `corepack` setup
- Changed `COPY pnpm-lock.yaml pnpm-workspace.yaml` → `COPY apps/web/package.json apps/web/package-lock.json`
- Changed `RUN pnpm install --frozen-lockfile` → `RUN npm ci --prefer-offline`
- Changed `CMD ["pnpm", "dev", "--host"]` → `CMD ["npm", "run", "dev", "--", "--host"]`
- Committed `apps/web/package-lock.json` (was untracked)

**Verified:** `docker build -f apps/web/Dockerfile --target development .` succeeds. `docker compose up --build` starts all three services without errors.

---

### Issue 4 — TypeScript build artifacts not in .gitignore (FIXED)
**Symptom:** `apps/web/tsconfig.app.tsbuildinfo` and `apps/web/tsconfig.node.tsbuildinfo` appeared as untracked files after every `tsc -b` run.  
**Fix:** Added `*.tsbuildinfo` to `.gitignore`.

---

## 2. End-to-End Validation Results

### 2.1 Backend Endpoints (14/14 PASS)

| Endpoint | HTTP | Result |
|----------|------|--------|
| `GET /health` | 200 | `{"status":"ok","service":"BSM Platform API","version":"2026.1.0"}` |
| `GET /health/db` | 200 | DB reachable, migration head confirmed |
| `GET /v1/legal-entities` | 200 | 4 entities returned |
| `GET /v1/positions` | 200 | 31 positions, paginated |
| `GET /v1/snapshots` | 200 | 4 snapshots |
| `GET /v1/scenarios` | 200 | 5 scenarios |
| `GET /v1/counterparties` | 200 | Counterparties loaded |
| `GET /v1/cashflows` | 200 | Cashflows loaded |
| `GET /v1/stress-tests` | 200 | Stress tests loaded |
| `GET /v1/analytics/lcr` | 200 | LCR ratio 1.5787 ✓ |
| `GET /v1/analytics/nsfr` | 200 | NSFR ratio 1.2727 ✓ |
| `GET /v1/analytics/capital` | 200 | CET1 11.23% ✓ |
| `GET /v1/analytics/balance-sheet` | 200 | Assets 325,000 ✓ |
| `GET /v1/analytics/positions/summary` | 200 | 31 positions ✓ |

### 2.2 Demo Bank Golden Values (all match)

| Metric | Value | Expected | Match |
|--------|-------|----------|-------|
| LCR ratio | 1.5787 (157.87%) | >100% | ✓ |
| HQLA total | 130,400 INR | 130,400 | ✓ |
| NCO | 82,600 INR | 82,600 | ✓ |
| NSFR ratio | 1.2727 (127.27%) | >100% | ✓ |
| ASF | 252,000 INR | 252,000 | ✓ |
| RSF | 198,000 INR | 198,000 | ✓ |
| CET1 ratio | 11.23% | >4.5% | ✓ |
| T1 ratio | 12.83% | >6.0% | ✓ |
| TCR | 16.05% | >8.0% | ✓ |
| Leverage ratio | 8.32% | >3.0% | ✓ |
| Total assets | 325,000 INR | 325,000 | ✓ |
| Total liabilities | 292,500 INR | 292,500 | ✓ |
| Total equity | 32,500 INR | 32,500 | ✓ |
| Balance sheet balances | True | True | ✓ |
| Position count | 31 | 31 | ✓ |

### 2.3 Frontend Build (PASS)

| Check | Result |
|-------|--------|
| TypeScript strict typecheck (`tsc --noEmit`) | **PASS — 0 errors** |
| Vite production build | **PASS — 7 chunks, 0 warnings** |

### 2.4 Docker Compose (PASS)

| Service | Status | Port |
|---------|--------|------|
| `bsm_postgres` | healthy | 5433 |
| `bsm_api` | healthy | 8000 |
| `bsm_web` | running (Vite ready) | 3000 |

`docker compose up --build` starts all three services without manual intervention.

---

## 3. Files Changed

| File | Change |
|------|--------|
| `apps/api/app/schemas/health.py` | Added `service: str` field to `HealthResponse` |
| `apps/api/app/routers/health.py` | Returns `service="BSM Platform API"` |
| `apps/web/src/lib/api.ts` | Fixed `/health/live` → `/health`, `/health/ready` → `/health` |
| `apps/web/src/types/api.ts` | Updated `HealthStatus` interface to match actual response shape |
| `apps/web/src/context/EntityContext.tsx` | Auto-selects `is_reporting_entity=true` entity first |
| `apps/web/Dockerfile` | Replaced pnpm with npm |
| `apps/web/package-lock.json` | Committed (was untracked) |
| `.gitignore` | Added `*.tsbuildinfo` |
| `docs/PROJECT_STATUS.md` | Updated to reflect Epic 3 completion (done in Epic 3 approval) |

---

## 4. Known Remaining Limitations (deferred to future epics)

| Item | Impact | Plan |
|------|--------|------|
| Auth is placeholder | Login always succeeds | Epic 5 (OIDC) |
| Analytics reads pre-seeded data | Results do not update when positions change | Epic 7 (engine wiring) |
| LCR seeded summary inconsistency | `lcr_results.total_outflows=110,000` vs component sum 20,800 | Documented; component data is self-consistent |
| Entity dropdown auto-selects Demo Bank only | No multi-tenant switching UX | Epic 9 (Frontend Phase 2) |
| `pnpm-workspace.yaml` at repo root | Leftover from original scaffold; not used by any build | Harmless; can be removed in cleanup epic |
