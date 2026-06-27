# Code Review Guidelines

## Non-Negotiables

These are hard blocks for any PR:

1. **Import boundary violations** — `import-linter` must pass. `reasoning/*` never imports `engines/*` or numpy/pandas. `engines/*` never imports `anthropic`.
2. **Floating-point in engines** — All monetary and regulatory calculations use `Decimal`. No `float`.
3. **Mutable domain models** — All domain models must have `model_config = {"frozen": True}`. No mutable state in `shared/domain/`.
4. **Untyped functions** — Every function in `shared/` and `apps/api/` must have full type annotations. `mypy --strict` must pass.
5. **Missing `ComputeRun` record** — Every engine execution must produce a persisted `ComputeRun` with `inputs_hash` and `outputs_hash`.
6. **Skipped audit log entry** — Every state-changing API call must produce an `AuditLogEntry`.
7. **Direct LLM calls in engine code** — Engines are deterministic Python. Zero Anthropic SDK calls in `engines/*`.

## Checklist (for every PR)

- [ ] CI is green (all 7 jobs pass)
- [ ] Import boundaries pass (`import-linter`)
- [ ] New engine code has golden test coverage
- [ ] New API endpoint has integration test coverage
- [ ] Alembic migration is reversible (has `downgrade()`)
- [ ] No secrets or credentials in committed files (gitleaks passes)
- [ ] `DECIMAL` used for all monetary amounts — no `float`
- [ ] New domain models are frozen Pydantic models

## Maker-Checker (SOD) Review

For PRs touching workflow, sign-off, or approval logic: explicitly verify that Preparer ≠ Reviewer ≠ Approver cannot be bypassed.

## Reasoning Module Review

For PRs touching `reasoning/*`: verify that the module returns a `ReasoningOutput` with `compute_run_ids` populated — every statement must be traceable to a compute run.
