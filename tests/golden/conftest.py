"""Golden test fixtures — determinism verification.

Golden tests verify that given the same inputs (snapshot + engine version),
the compute layer produces bit-identical outputs across runs and code changes.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


GOLDEN_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def golden_dir() -> Path:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    return GOLDEN_DIR


@pytest.fixture
def load_golden(golden_dir: Path):
    """Return a loader that reads a JSON golden fixture by name."""
    def _load(name: str) -> dict:
        path = golden_dir / f"{name}.json"
        if not path.exists():
            pytest.skip(f"Golden fixture not yet generated: {name}.json")
        with path.open() as f:
            return json.load(f)
    return _load
