# BSM Platform — Administrator Guide

> **Version:** v1.0-demo  
> **Audience:** System Administrators, DevOps Engineers, Technical Leads

---

## System Requirements

### Minimum
- CPU: 4 cores
- RAM: 8 GB
- Storage: 20 GB
- OS: Ubuntu 22.04, macOS 13+, or Windows 11 with WSL2

### Recommended (Production)
- CPU: 8 cores
- RAM: 16 GB
- Storage: 100 GB SSD
- PostgreSQL 16+

---

## Local Development Setup

### Prerequisites
```bash
# Required tools
node >= 20
python >= 3.12
uv >= 0.4.0
docker & docker compose
```

### Install Dependencies
```bash
# From project root
uv sync                          # Python dependencies
cd apps/web && npm install       # Frontend dependencies
```

### Environment Variables
Create `apps/api/.env`:
```env
DATABASE_URL=postgresql+asyncpg://bsm:bsm@localhost:5432/bsm
ANTHROPIC_API_KEY=sk-ant-...
APP_MODE=local
SECRET_KEY=dev-secret-key-change-in-production
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["http://localhost:3000"]
```

### Start Services
```bash
# Start PostgreSQL
docker compose up -d postgres

# Run migrations
cd apps/api && alembic upgrade head

# Seed demo data (optional)
python -m app.scripts.seed

# Start API
uvicorn app.main:app --reload --port 8000

# Start frontend (separate terminal)
cd apps/web && npm run dev
```

---

## Docker Compose Deployment

```bash
# Full stack
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f api
docker compose logs -f web
```

### docker-compose.yml Services
- `postgres` — PostgreSQL 16 database
- `api` — FastAPI application (port 8000)
- `web` — React frontend served by nginx (port 3000)

---

## Database Management

### Migrations
```bash
# Apply all migrations
alembic upgrade head

# Check current revision
alembic current

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Seed Demo Data
```bash
python -m app.scripts.seed
```

This creates:
- Demo Bank legal entity (reporting entity)
- 10 demo positions (mixed asset classes)
- 3 historical snapshots (Q2, Q3, Q4 2025)
- Computed analytics for all 3 snapshots

---

## Autonomous Monitoring

The scheduler starts automatically with the API (FastAPI lifespan). Check status:

```bash
GET /v1/autonomous/status
```

Trigger manual run:
```bash
POST /v1/autonomous/monitor/run
```

### Scheduler Configuration
In `apps/api/app/services/ai/autonomous/scheduler.py`:
```python
MONITORING_INTERVAL_SECONDS = 900  # 15 minutes
```

Morning briefings fire at 06:00–06:14 UTC daily.

---

## API Configuration

### Production Checklist
- [ ] `APP_MODE=production` (disables /docs endpoint)
- [ ] `SECRET_KEY` — random 32+ char string
- [ ] `ANTHROPIC_API_KEY` — valid Anthropic API key
- [ ] `DATABASE_URL` — production PostgreSQL connection
- [ ] `ALLOWED_ORIGINS` — restrict to your domain
- [ ] TLS termination via nginx/load balancer
- [ ] Rate limiting on API gateway

---

## Monitoring and Observability

The API exposes OpenTelemetry traces. Configure an OTLP endpoint:
```env
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
OTEL_SERVICE_NAME=bsm-api
```

### Health Check
```bash
GET /healthz
```

---

## Backup and Recovery

### Database Backup
```bash
pg_dump bsm | gzip > bsm_backup_$(date +%Y%m%d).sql.gz
```

### Restore
```bash
gunzip -c bsm_backup_20260101.sql.gz | psql bsm
```

---

## Security Hardening

1. **Network:** Place API behind a reverse proxy. Never expose PostgreSQL publicly.
2. **Auth:** Current demo uses simple token auth. Replace with OAuth2/OIDC for production.
3. **API key:** Store `ANTHROPIC_API_KEY` in a secrets manager (AWS Secrets Manager, HashiCorp Vault).
4. **TLS:** Enforce HTTPS everywhere. Use Let's Encrypt or corporate CA.
5. **CORS:** Restrict `ALLOWED_ORIGINS` to your specific domains.
6. **Logging:** All API requests and AI tool calls are logged with structlog. Route to your SIEM.

---

## User Management

Currently the platform uses a demo authentication mode (any credentials accepted). For production:
1. Implement JWT-based authentication in `apps/api/app/routers/auth.py`
2. Add user management tables via a new Alembic migration
3. Update `AuthContext.tsx` to use real API tokens

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| API returns 500 | DB connection failure | Check `DATABASE_URL`, verify PostgreSQL is running |
| `alembic upgrade` fails | Migration conflict | Run `alembic heads` to check for multiple heads |
| No entities in UI | Empty database | Run seed script |
| SAM returns "no data" | No snapshots computed | Create snapshot + run engines |
| Scheduler not running | API not started | Check API logs for `autonomous_scheduler_task_started` |
| High memory usage | Too many background queries | Check monitoring interval, reduce if needed |
