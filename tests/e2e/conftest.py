"""End-to-end test fixtures — requires full Docker stack."""
from __future__ import annotations

import os
import httpx
import pytest


BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def api_client() -> httpx.Client:
    """Synchronous HTTP client pointed at the running API."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
def health_check(api_client: httpx.Client) -> None:
    """Assert the API is reachable before running e2e tests."""
    response = api_client.get("/health")
    assert response.status_code == 200, (
        f"API not healthy at {BASE_URL}. "
        "Start the stack with: docker compose up -d"
    )
