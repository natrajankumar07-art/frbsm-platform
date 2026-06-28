"""
OpenTelemetry initialisation.

Wires up tracing with OTLP export when an endpoint is configured.
Falls back to a no-op provider when running locally without a collector.

Call setup_telemetry(settings) once inside the lifespan startup, after
logging is configured but before the first request is served.
"""

import structlog
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = structlog.get_logger(__name__)

_NOOP_ENDPOINT_PREFIXES = ("", "http://localhost", "http://127.0.0.1")


def setup_telemetry(
    *,
    service_name: str,
    otlp_endpoint: str,
    db_url: str,
) -> None:
    """
    Initialise OpenTelemetry tracing.

    If otlp_endpoint is empty or points at localhost (no real collector
    configured), a no-op provider is registered so spans are simply dropped.
    """
    if any(otlp_endpoint.startswith(p) for p in _NOOP_ENDPOINT_PREFIXES):
        logger.info(
            "otel_noop",
            reason="No OTLP collector configured — tracing disabled for local mode.",
        )
        trace.set_tracer_provider(TracerProvider())
        return

    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        logger.info("otel_configured", endpoint=otlp_endpoint, service=service_name)
    except Exception:
        logger.warning("otel_setup_failed", exc_info=True)
        trace.set_tracer_provider(TracerProvider())


def instrument_fastapi(app: object) -> None:
    """Attach FastAPI auto-instrumentation to the running app."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)  # type: ignore[arg-type]
        logger.info("otel_fastapi_instrumented")
    except Exception:
        logger.warning("otel_fastapi_instrument_failed", exc_info=True)


def instrument_sqlalchemy(engine: object) -> None:
    """
    Attach SQLAlchemy auto-instrumentation to the async engine.

    The OTel SQLAlchemy instrumentor requires a sync engine. For async engines
    the underlying sync engine is accessible via engine.sync_engine.
    """
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from sqlalchemy.ext.asyncio import AsyncEngine

        sync_engine = engine.sync_engine if isinstance(engine, AsyncEngine) else engine  # type: ignore[union-attr]
        SQLAlchemyInstrumentor().instrument(engine=sync_engine)  # type: ignore[arg-type]
        logger.info("otel_sqlalchemy_instrumented")
    except Exception:
        logger.warning("otel_sqlalchemy_instrument_failed", exc_info=True)
