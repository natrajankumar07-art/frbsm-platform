# BSM Platform — Deployment Guide

> **Version:** v1.0-demo  
> **Audience:** DevOps Engineers, Platform Engineers, IT Operations

---

## Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Docker | 24.x |
| Docker Compose | v2.x |
| Node.js | 20.x (local dev only) |
| Python | 3.12 (local dev only) |
| uv | 0.4.0 (local dev only) |
| PostgreSQL | 16 (managed by Docker in standard deployment) |

---

## Local Development

### 1. Clone and install
```bash
git clone <repo-url> frbsm-platform
cd frbsm-platform

# Python dependencies
uv sync

# Frontend dependencies
cd apps/web && npm install && cd ../..
```

### 2. Configure environment
```bash
cp apps/api/.env.example apps/api/.env
```

Edit `apps/api/.env`:
```env
DATABASE_URL=postgresql+asyncpg://bsm:bsm@localhost:5432/bsm
ANTHROPIC_API_KEY=sk-ant-...
APP_MODE=local
SECRET_KEY=dev-secret-32-chars-min
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["http://localhost:3000"]
```

### 3. Start database
```bash
docker compose up -d postgres
```

### 4. Run migrations and seed
```bash
cd apps/api
alembic upgrade head
python -m app.scripts.seed
```

### 5. Start services
```bash
# Terminal 1 — API
cd apps/api
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd apps/web
npm run dev
```

Platform available at: `http://localhost:3000`  
API docs at: `http://localhost:8000/docs`

---

## Docker Compose (Recommended)

### Standard deployment
```bash
docker compose up -d
```

This starts:
- `postgres` — PostgreSQL 16 on port 5432
- `api` — FastAPI on port 8000
- `web` — React (nginx) on port 3000

### Check status
```bash
docker compose ps
docker compose logs -f api
```

### First-time database setup
```bash
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.seed
```

### Stop
```bash
docker compose down
```

### Full reset (destroys all data)
```bash
docker compose down -v
```

---

## Production Deployment

### Environment Variables (Production)
```env
DATABASE_URL=postgresql+asyncpg://bsm_user:strong_password@db-host:5432/bsm_prod
ANTHROPIC_API_KEY=sk-ant-...        # Store in secrets manager
APP_MODE=production                  # Disables /docs endpoint
SECRET_KEY=<random 64-char string>
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=["https://bsmplatform.yourdomain.com"]
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
OTEL_SERVICE_NAME=bsm-api
```

### Production Checklist
- [ ] `APP_MODE=production`
- [ ] `SECRET_KEY` — cryptographically random, 64+ chars
- [ ] `ANTHROPIC_API_KEY` — stored in AWS Secrets Manager / HashiCorp Vault, not in `.env`
- [ ] `DATABASE_URL` — points to managed PostgreSQL (RDS, Cloud SQL, etc.)
- [ ] `ALLOWED_ORIGINS` — locked to your domain(s)
- [ ] TLS terminated at load balancer / nginx
- [ ] API port (8000) not publicly exposed — only via reverse proxy
- [ ] PostgreSQL not publicly exposed
- [ ] Health check endpoint monitored: `GET /healthz`
- [ ] Log forwarding to SIEM configured

### nginx reverse proxy (example)
```nginx
server {
    listen 443 ssl;
    server_name bsmplatform.yourdomain.com;

    location /api/ {
        proxy_pass http://api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://web:3000/;
    }
}
```

---

## Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Check current state
alembic current

# View history
alembic history --verbose

# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade 0015
```

### Creating a new migration
```bash
alembic revision --autogenerate -m "add_my_table"
# Review the generated file in alembic/versions/
alembic upgrade head
```

---

## Frontend Build

```bash
cd apps/web

# Production build
npm run build

# Preview build locally
npm run preview

# Type check
npm run typecheck
```

Build output: `apps/web/dist/`  
Serve with nginx or any static host (S3 + CloudFront, etc.).

---

## Backup and Recovery

### Backup database
```bash
# From the host
pg_dump -h localhost -U bsm bsm | gzip > bsm_$(date +%Y%m%d_%H%M%S).sql.gz

# Via Docker
docker compose exec postgres pg_dump -U bsm bsm | gzip > bsm_backup.sql.gz
```

### Restore
```bash
gunzip -c bsm_backup.sql.gz | psql -h localhost -U bsm bsm
```

### Automated backups (cron example)
```bash
# /etc/cron.d/bsm-backup
0 2 * * * docker exec bsm-postgres pg_dump -U bsm bsm | gzip > /backups/bsm_$(date +\%Y\%m\%d).sql.gz
```

---

## Monitoring

### Health endpoint
```
GET /healthz
→ { "status": "ok", "db": "ok", "version": "1.0.0" }
```

### Autonomous scheduler status
```
GET /v1/autonomous/status
```

### OpenTelemetry (Jaeger)
```bash
docker compose up -d jaeger
# UI at http://localhost:16686
```

### Logs
All API logs are structured JSON (structlog). Forward to your log aggregator:
```bash
docker compose logs api --follow | your-log-forwarder
```

---

## Troubleshooting

| Symptom | Check | Fix |
|---------|-------|-----|
| API returns 500 | `docker compose logs api` | Check `DATABASE_URL` and Postgres connectivity |
| Alembic error on upgrade | `alembic heads` | Resolve multiple heads with a merge migration |
| No data in UI | Entity selector empty | Run `python -m app.scripts.seed` |
| SAM responses slow | Anthropic API latency | Check `ANTHROPIC_API_KEY` validity; check Anthropic status |
| Autonomous scheduler not running | API startup logs | Look for `autonomous_scheduler_task_started` in logs |
| Frontend build fails | `npm run typecheck` | Fix TypeScript errors before building |
| Port conflict on 3000 or 8000 | `lsof -i :3000` | Kill conflicting process or change port in compose |
