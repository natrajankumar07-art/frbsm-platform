"""
FastAPI dependency providers.

Import these in route handlers:

    from app.dependencies import DBSession, AppSettings

    @router.get("/example")
    async def example(db: DBSession, cfg: AppSettings) -> ...:
        ...
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .config import Settings, settings as _settings
from .db.session import async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a transactional async DB session; commits on success, rolls back on error."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_settings() -> Settings:
    """Return the application settings singleton."""
    return _settings


# Convenience type aliases for use in route signatures
DBSession = Annotated[AsyncSession, Depends(get_db_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]
