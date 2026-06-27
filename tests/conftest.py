"""Root conftest — fixtures available to all test suites."""
from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio as the anyio backend for all async tests."""
    return "asyncio"
