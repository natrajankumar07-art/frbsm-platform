# Architecture

## Overview

BSM Platform is a **modular monolith**: a single deployable FastAPI service that imports all compute engines as Python packages. There are no microservices.

## Two-Layer Architecture

```
┌─────────────────────────────────────────────────────┐
│  Reasoning Layer (Claude / LLM)                      │
│  – Interprets outputs, writes disclosures, explains  │
│  – NEVER computes regulatory numbers                 │
│  – reasoning/modules/*.py                            │
└────────────────────┬────────────────────────────────┘
                     │ reads ComputeRun outputs
┌────────────────────▼────────────────────────────────┐
│  Compute Layer (Python engines)                      │
│  – Deterministic, auditable, unit-tested             │
│  – engines/credit/, engines/capital/, ...            │
│  – Called by FastAPI endpoints, NOT by Claude        │
└─────────────────────────────────────────────────────┘
```

## Import Boundaries

Enforced by `import-linter` in CI. Violations fail the build.

| Rule | Source | Forbidden Target |
|------|--------|-----------------|
| Reasoning cannot import engines | `reasoning/*` | `engines/*` |
| Reasoning cannot use numpy/pandas | `reasoning/*` | `numpy`, `pandas` |
| Engines cannot import reasoning | `engines/*` | `reasoning/*` |
| Engines cannot use Anthropic SDK | `engines/*` | `anthropic` |
| API layer cannot bypass engines | `app.api.*` | `engines.*` direct |

## Data Flow

```
User uploads positions
      │
      ▼
Snapshot created (DRAFT)
      │
      ▼
Snapshot locked (LOCKED) — position_hash computed, immutable
      │
      ▼
Compute engines run → ComputeRun stored with inputs_hash + outputs_hash
      │
      ▼
Reasoning modules read ComputeRun → ReasoningRun stored
      │
      ▼
Workpaper assembled → Maker-checker workflow → Filed (FILED)
```

## Determinism Guarantee

Same snapshot + same engine version → bit-identical outputs.

- All engine inputs are SHA-256 hashed before the run.
- All engine outputs are SHA-256 hashed and stored in `ComputeRun`.
- Golden tests verify hash stability across code changes.

## Audit Log

Append-only PostgreSQL table with a DDL trigger that rejects UPDATE and DELETE at the database level. Entries are SHA-256 hash-chained (each entry stores the hash of the previous entry).

## Modules

Detailed documentation for each engine and reasoning module is in `docs/engines/` and `docs/reasoning/` (created in Epic 1+).
