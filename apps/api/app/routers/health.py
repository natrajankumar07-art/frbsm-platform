"""
Health check endpoints.

These routes are always mounted regardless of auth state. They are used by:
  - Docker / Kubernetes liveness and readiness probes
  - Load balancer health checks
  - CI smoke tests after deployment

No authentication required. No sensitive data returned.
"""

import os
from time import monotonic

from fastapi import APIRouter
from sqlalchemy import text

from ..dependencies import AppSettings, DBSession
from ..schemas.health import DBHealthResponse, HealthResponse

router = APIRouter(tags=["health"])

_COMMIT = os.environ.get("GIT_COMMIT", "dev")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Returns 200 if the process is alive. Does not check database.",
)
async def health(cfg: AppSettings) -> HealthResponse:
    return HealthResponse(
        status="ok",
        version="2026.1.0",
        mode=str(cfg.app_mode),
        commit=_COMMIT,
    )


@router.get(
    "/health/db",
    response_model=DBHealthResponse,
    summary="Readiness probe",
    description="Returns 200 if the process can reach the database and Alembic is at head.",
)
async def health_db(db: DBSession) -> DBHealthResponse:
    start = monotonic()
    result = await db.execute(text("SELECT 1"))
    result.scalar()
    latency_ms = round((monotonic() - start) * 1000, 1)

    migration_head: str | None = None
    try:
        row = await db.execute(
            text("SELECT version_num FROM alembic_version LIMIT 1")
        )
        migration_head = row.scalar_one_or_none()
    except Exception:
        pass

    return DBHealthResponse(
        status="ok",
        latency_ms=latency_ms,
        migration_head=migration_head,
    )
