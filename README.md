# BSM Platform

Bank Supervisory Management — regulatory capital, liquidity, and IFRS 9 reporting platform.

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY at minimum

# 2. Start the development stack
docker compose up -d

# 3. Run database migrations
docker compose exec api alembic upgrade head

# 4. Open the web app
open http://localhost:3000
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design.

**Key constraint:** The reasoning layer (Claude) never computes regulatory numbers. The compute engines (Python) compute them; Claude explains and reasons about them.

## Development

```bash
# Python — install with uv
uv sync --all-extras

# Frontend — install with pnpm
pnpm install

# Run all checks
uv run pytest tests/unit/
uv run mypy shared/ apps/api/
cd apps/web && pnpm type-check && pnpm lint
```

## Project Layout

| Directory | Purpose |
|-----------|---------|
| `apps/api/` | FastAPI application |
| `apps/web/` | React frontend |
| `apps/workers/` | Background task workers |
| `engines/` | Compute engines (Python packages) |
| `reasoning/` | Claude reasoning modules |
| `shared/` | Shared Python packages (domain, audit, testing, utils) |
| `tests/` | All test suites |
| `ops/` | Infrastructure and deployment |
| `docs/` | Project documentation |
| `data/demo/` | Generated demo data (not committed) |
| `tools/` | Developer tooling scripts |
