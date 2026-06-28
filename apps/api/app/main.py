"""
FastAPI application factory.

Startup order:
  1. Logging (structlog) — must be first so all subsequent logs are formatted
  2. OpenTelemetry — traces must be active before any routes handle requests
  3. FastAPI app creation — title, docs, version
  4. Middleware registration — outermost first (request ID → CORS)
  5. Exception handlers
  6. Router inclusion
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from .logging import configure_logging
from .middleware import RequestIDMiddleware
from .routers import health as health_router
from .telemetry import instrument_fastapi, instrument_sqlalchemy, setup_telemetry

# ---------------------------------------------------------------------------
# Logging — configure before the first logger call
# ---------------------------------------------------------------------------
configure_logging(
    log_level=settings.log_level,
    json_logs=settings.app_mode.value in ("production", "staging"),
)

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from .db.session import engine

    logger.info(
        "bsm_api_starting",
        mode=settings.app_mode,
        debug=settings.debug,
    )

    setup_telemetry(
        service_name=settings.otel_service_name,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        db_url=settings.database_url,
    )
    instrument_fastapi(app)
    instrument_sqlalchemy(engine)

    logger.info("bsm_api_ready")
    yield

    logger.info("bsm_api_stopping")
    await engine.dispose()
    logger.info("bsm_api_stopped")


# ---------------------------------------------------------------------------
# Determine docs visibility
# docs are available in local + staging; disabled in production unless debug
# ---------------------------------------------------------------------------
_show_docs = settings.debug or settings.app_mode.value in ("local", "staging", "demo")

app = FastAPI(
    title="BSM Platform API",
    description=(
        "AI-Powered Balance Sheet Management & Regulatory Reporting Platform.\n\n"
        "The LLM never computes regulatory numbers — Python computes them; "
        "Claude explains and reasons about them."
    ),
    version="2026.1.0",
    docs_url="/docs" if _show_docs else None,
    redoc_url="/redoc" if _show_docs else None,
    openapi_url="/openapi.json" if _show_docs else None,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware — outermost added last (executed first)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Demo-Mode"],
)

# RequestIDMiddleware must be inside CORS so the response header is visible
app.add_middleware(RequestIDMiddleware)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(health_router.router)
