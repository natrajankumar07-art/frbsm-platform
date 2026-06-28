"""
Structured logging configuration using structlog.

Call configure_logging() once at application startup, before any log statements.
All loggers then emit JSON in production and pretty-printed output locally.
"""

import logging
import sys

import structlog


def configure_logging(log_level: str = "INFO", *, json_logs: bool) -> None:
    """
    Configure structlog and stdlib logging to use a unified processor chain.

    json_logs=True  → machine-readable JSON (production/staging)
    json_logs=False → human-readable colored output (local/debug)
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level.upper())

    # Suppress noisy third-party loggers
    for name in ("uvicorn.access", "watchfiles.main"):
        logging.getLogger(name).setLevel(logging.WARNING)
