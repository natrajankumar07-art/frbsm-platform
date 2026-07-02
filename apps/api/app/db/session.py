"""Async SQLAlchemy engine and session factory."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..config import settings
from urllib.parse import urlparse
import logging
# echo=False even in debug mode — SQL logging via structlog is handled by
# the OTel SQLAlchemy instrumentor; SQLAlchemy's own echo is too noisy.
# Set SQL_ECHO=true in .env only when you need raw statement tracing.
import os as _os

parsed = urlparse(settings.database_url)
logging.warning("Database URL: %s", settings.database_url)
logging.warning("Database host: %s", parsed.hostname)
logging.warning("Database port: %s", parsed.port)

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=_os.getenv("SQL_ECHO", "false").lower() == "true",
    future=True,
)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
