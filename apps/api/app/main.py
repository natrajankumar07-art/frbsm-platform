"""FastAPI application factory and lifespan management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.session import engine

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle."""
    logger.info(
        "bsm_api_starting",
        mode=settings.app_mode,
        debug=settings.debug,
    )
    # Future sprints will add: OTel tracer init, connection pool warmup, etc.
    yield
    logger.info("bsm_api_stopping")
    await engine.dispose()


app = FastAPI(
    title="BSM Platform API",
    description="AI-Powered Balance Sheet Management & Regulatory Reporting Platform",
    version="2026.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Demo-Mode"],
)


# ---------------------------------------------------------------------------
# Health endpoints — always available, no auth required
# ---------------------------------------------------------------------------
@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "2026.1.0", "mode": settings.app_mode}


@app.get("/health/db", tags=["health"])
async def health_db() -> dict[str, object]:
    """Verify database connectivity. Used by load balancer health checks."""
    from time import monotonic

    from sqlalchemy import text

    from .db.session import async_session_factory

    start = monotonic()
    async with async_session_factory() as session:
        await session.execute(text("SELECT 1"))
    latency_ms = round((monotonic() - start) * 1000, 1)
    return {"status": "ok", "latency_ms": latency_ms}
