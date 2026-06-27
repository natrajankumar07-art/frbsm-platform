# Repository Reconciliation

**Purpose:** Consolidate the platform's current multi-repository layout into a single, coherent monorepo structure aligned with the architecture in `Final_Build_Pack.md`.

**Status:** Migration plan
**Target Completion:** End of Phase 26
**Risk Level:** Medium (touches every developer's workflow)

---

## 1. Background

The platform was bootstrapped across several repositories owned by different teams. As modules matured, boundaries blurred, duplicated utilities appeared, and the calculation/reasoning separation became harder to enforce across repos. The reconciliation merges these into one repository with strict module boundaries.

### 1.1 Current State (Pre-Reconciliation)

| Repo | Owner | Contents | Status |
|---|---|---|---|
| `bsm-core` | Platform | Position store, snapshot engine, base API | Active |
| `bsm-regcalc` | Reg Tech | RWA, capital, leverage engines | Active |
| `bsm-liquidity` | ALM | LCR, NSFR engines | Active |
| `bsm-alm` | ALM | Gap, EVE, NII, FTP, IRRBB | Active |
| `bsm-ifrs9` | Credit | Staging, ECL engine | Active |
| `bsm-stress` | Risk | Scenario engine | Active |
| `bsm-llm` | AI | Reasoning modules, prompts, eval harness | Active |
| `bsm-ui` | Frontend | React app | Active |
| `bsm-reports` | Reporting | Templates, exporters | Active |
| `bsm-shared` | Platform | Domain models, audit utilities | Active |
| `bsm-data` | Data | Ingest, reference data | Active |
| `bsm-infra` | SRE | Terraform, k8s, helm | Stays separate |
| `bsm-docs` | All | Documentation | Migrated into monorepo |

### 1.2 Problems With Current State

- **Duplicated domain models:** `Position`, `Counterparty`, `Snapshot` defined in three repos with subtle drift.
- **Inconsistent versioning:** engines released independently; consumers pin different versions.
- **Cross-repo refactors are painful:** a domain change requires PRs across 6 repos.
- **CI fragmentation:** golden tests in `bsm-regcalc` cannot verify reasoning outputs in `bsm-llm`.
- **Boundary leakage:** `bsm-llm` has begun importing calculation utilities; risks LLM substituting for compute.
- **Audit log split:** different repos write to different audit sinks, making lineage harder to trace.

---

## 2. Target State (Post-Reconciliation)

### 2.1 Single Monorepo: `platform/`

Layout per `Final_Build_Pack.md` §11. Repeated here for reference:

```
platform/
├── apps/
│   ├── api/
│   ├── web/
│   └── workers/
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
├── reports/
├── workflow/
├── observability/
├── shared/
│   ├── domain/
│   ├── audit/
│   └── testing/
├── tests/
│   ├── golden/
│   ├── property/
│   └── e2e/
└── docs/
```

### 2.2 What Stays Separate

- `platform-infra` (Terraform, k8s manifests, Helm charts) — different release cadence, different reviewers, different blast radius.
- `platform-data-samples` (large synthetic datasets for testing) — kept in Git LFS or object storage with pointers in the monorepo.

### 2.3 Module Boundary Rules

The reconciliation is the moment to enforce, in code, the architectural separation:

| Rule | Enforcement |
|---|---|
| `reasoning/*` may not import from `engines/*` directly | Import linter rule |
| `reasoning/*` may not import numerical libraries (`numpy`, `pandas`) | Dependency scanner |
| `engines/*` may not import from `reasoning/*` | Import linter rule |
| `engines/*` may not call Anthropic API | Network egress policy in CI |
| `reports/*` may format outputs but never compute new numerics | Code review checklist + grep gates |
| Every engine exposes a single public `compute()` entrypoint | Module init test |
| All shared domain types live in `shared/domain` | Import linter rule |

Import linting will be done with `import-linter` (Python) configured in `.importlinter.toml`.

---

## 3. Source-to-Target Mapping

### 3.1 Repo → Path Mapping

| Source Repo | Target Path in `platform/` |
|---|---|
| `bsm-core` | `data/`, `apps/api/` (base routes), `shared/audit/` |
| `bsm-regcalc` | `engines/rwa/`, `engines/capital/` |
| `bsm-liquidity` | `engines/liquidity/` |
| `bsm-alm` | `engines/alm/`, `engines/ftp/`, `engines/irrbb/` |
| `bsm-ifrs9` | `engines/ecl/` |
| `bsm-stress` | `engines/stress/` |
| `bsm-llm` | `reasoning/`, `tests/eval_harness/` |
| `bsm-ui` | `apps/web/` |
| `bsm-reports` | `reports/` |
| `bsm-shared` | `shared/domain/`, `shared/testing/` |
| `bsm-data` | `data/ingest/`, `data/reference/` |
| `bsm-docs` | `docs/` |

### 3.2 Duplicated Module Resolution

The following modules exist in multiple repos with drift. Reconciliation rules:

| Module | Source of Truth | Action |
|---|---|---|
| `Position` model | `bsm-shared` | Adopt as canonical; remove copies from `bsm-core`, `bsm-regcalc` |
| `Counterparty` model | `bsm-shared` | Same |
| `Snapshot` model | `bsm-core` | Promote to `shared/domain/`; remove copies |
| Audit logger | `bsm-shared` | Promote to `shared/audit/`; remove copies in 4 other repos |
| Date / business-day utilities | `bsm-core` | Promote to `shared/utils/`; reconcile differences with `bsm-alm` version |
| Currency / FX conversion | `bsm-regcalc` | Promote to `shared/utils/`; reconcile with `bsm-alm` and `bsm-liquidity` versions |
| Risk weight tables | `bsm-regcalc` | Stays in `engines/rwa/reference/`; not shared (jurisdiction-specific) |
| HQLA classification | `bsm-liquidity` | Stays in `engines/liquidity/` |

Drift-resolution policy: where versions differ, the version with the most recent golden test coverage wins. Where coverage is equal, the version with the most recent regulatory citation wins. All drift resolutions documented in `docs/reconciliation/drift_resolutions.md`.

---

## 4. Migration Plan

### 4.1 Phases

The reconciliation runs as a 6-week effort, parallel to active development.

**Week 1 — Preparation**
- Create `platform/` monorepo skeleton with target layout
- Set up CI (single pipeline replacing 13 separate ones)
- Configure import linter and dependency rules
- Migrate `docs/` (lowest-risk move)
- Migrate `shared/` (foundational, blocks everything else)

**Week 2 — Engines (Tranche 1)**
- Migrate `engines/rwa`, `engines/capital`, `engines/liquidity`
- For each: copy code, update imports, port tests, verify golden tests pass
- Original repos enter read-only mode but remain accessible

**Week 3 — Engines (Tranche 2)**
- Migrate `engines/ecl`, `engines/alm`, `engines/ftp`, `engines/irrbb`, `engines/stress`

**Week 4 — Reasoning, Data, Reports**
- Migrate `reasoning/` (with strict boundary enforcement; this is where rules in §2.3 are most important)
- Migrate `data/` and `reports/`

**Week 5 — Apps**
- Migrate `apps/api/`, `apps/web/`, `apps/workers/`
- Reconnect to monorepo'd backend

**Week 6 — Cleanup & Lock**
- Archive original repos (read-only, retained for audit trail)
- Decommission old CI pipelines
- Update all developer onboarding docs
- Run full end-to-end test against historical reporting dates; require bit-identical reproduction

### 4.2 Migration Mechanics

For each module migration:

1. Run `git filter-repo` on source repo to preserve history of moved paths
2. Merge into monorepo with `git read-tree` to land at target path
3. Update import paths via `ruff --fix` plus codemods in `tools/migration/`
4. Run module's own test suite against new location
5. Run golden tests
6. Run determinism test (same snapshot → same outputs as pre-migration)
7. Open PR; require sign-off from both source and target module owner

History preservation: every commit must remain traceable through the migration. Use `git filter-repo` with `--path` rewrites, not naive copy-paste.

### 4.3 Coexistence Period

During migration weeks 2–5, the source repos and monorepo coexist:

- Source repos: bug-fix only, no new features
- Monorepo: new features land here
- Daily sync job mirrors any source-repo bug fix into monorepo within 24 hours
- After a module is migrated, its source repo is frozen and marked read-only

---

## 5. CI Reconciliation

### 5.1 Before

- 13 separate CI pipelines across GitHub Actions, GitLab CI, Jenkins
- Inconsistent test selection, lint rules, security scanning
- Engine-to-engine integration tested only at staging

### 5.2 After

Single CI pipeline in `.github/workflows/`:

| Job | Trigger | Duration Budget |
|---|---|---|
| `lint` | every PR | 2 min |
| `typecheck` | every PR | 3 min |
| `unit` | every PR | 8 min |
| `golden` | every PR touching `engines/*` | 15 min |
| `property` | every PR touching `engines/*` | 10 min |
| `reasoning-eval` | every PR touching `reasoning/*` | 20 min |
| `integration` | every PR | 25 min |
| `e2e` | nightly + on release | 90 min |
| `determinism` | nightly | 60 min |
| `security` | every PR | 5 min |
| `deps` | every PR | 3 min |

**Test selection:** `pytest --testmon` and `nx affected` (for the frontend) keep PR time bounded; nightly runs everything regardless.

**Required checks for merge to `main`:** `lint`, `typecheck`, `unit`, plus all jobs whose scope is touched by the diff.

---

## 6. Reasoning Layer Boundary — Special Attention

Because the LLM/Python separation is the most important architectural invariant, reconciliation includes hard boundary enforcement for `reasoning/`:

1. **Import boundary:** `reasoning/*` may import only from `shared/domain/`, `shared/utils/`, and third-party libraries on an allowlist.
2. **Banned imports:** `numpy`, `pandas`, `scipy`, `engines/*`. CI fails the build if any of these appear in `reasoning/*`.
3. **Network boundary:** `reasoning/*` may call Anthropic API and nothing else. Egress allowlist enforced in test container.
4. **Output contract:** every reasoning module returns a typed `ReasoningOutput` with required fields: `text`, `compute_run_ids[]`, `model_version`, `prompt_hash`. Modules that don't comply fail integration tests.
5. **No silent fallbacks:** if a required compute output is missing, the reasoning module raises; it does not fabricate.

These rules are also part of code review checklist (see `docs/contributing/code_review.md`).

---

## 7. Risk Register for the Reconciliation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| History loss during migration | Low | High | Use `git filter-repo`, verify with sample commits |
| Golden test regression | Medium | High | Run golden suite before and after each module move; bit-identical required |
| Developer disruption | High | Medium | Migration playbook, daily standup during weeks 1–6 |
| CI capacity overflow | Medium | Medium | Increase runner pool for migration weeks |
| Hidden cross-repo dependency | Medium | Medium | Pre-migration dependency graph audit; surface in week 0 |
| Boundary rule breaks existing reasoning module | Medium | Medium | Pre-flight grep + fix; allow temporary exemptions documented in `.importlinter.toml` with expiry date |
| Performance regression from monorepo build | Low | Low | Bazel/Pants only if needed; start with simple uv + pnpm workspace |

---

## 8. Acceptance Criteria

The reconciliation is complete when all of the following are true:

1. All modules listed in §3.1 live at their target paths.
2. All boundary linting rules in §2.3 pass.
3. The full golden test suite passes against the monorepo, including bit-identical reproduction of the prior month's filed regulatory returns.
4. The full determinism test passes (same snapshot, same code, same output hash).
5. All 13 source repositories are archived and read-only.
6. A single CI pipeline replaces the 13 prior ones.
7. Developer onboarding doc references only the monorepo.
8. No `reasoning/*` module imports a numerical library or calls into `engines/*`.

---

## 9. Post-Reconciliation Maintenance

Once consolidated, the following practices prevent re-fragmentation:

- New modules added inside `platform/` only; spinning out a separate repo requires architecture approval
- Quarterly dependency hygiene review (de-duplicate utilities)
- Boundary lint rules treated as production code (changes require review)
- All cross-module refactors land as single PRs (no multi-PR coordination)

---

## 10. Companion Documents

- `Final_Build_Pack.md` — overall architecture
- `Phase27.md` — productionisation phase (consumes the reconciled repo)
- `docs/reconciliation/drift_resolutions.md` — module-by-module drift decisions (created during migration)
- `docs/reconciliation/migration_log.md` — week-by-week migration record

---

*End of Repository Reconciliation.*
