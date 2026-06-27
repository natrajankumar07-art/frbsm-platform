"""Property test fixtures — Hypothesis-based invariant testing."""
from __future__ import annotations

import pytest
from hypothesis import settings, HealthCheck

# Suppress the slow-data health check on CI where filesystem I/O is variable
settings.register_profile(
    "ci",
    max_examples=200,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.register_profile("dev", max_examples=50)
settings.load_profile("ci")
