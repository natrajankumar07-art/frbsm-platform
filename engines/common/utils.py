"""Shared utilities for all compute engines."""

from __future__ import annotations

import hashlib
import json
from decimal import ROUND_HALF_UP, Decimal
from typing import Any


def canonical_hash(data: Any) -> str:
    """SHA-256 of a canonical JSON serialisation (sort_keys, Decimal→str)."""
    serialised = json.dumps(data, sort_keys=True, default=str, ensure_ascii=True)
    return hashlib.sha256(serialised.encode()).hexdigest()


def quantize(value: Decimal, places: int = 8) -> Decimal:
    """Round a Decimal to *places* decimal places using banker's rounding."""
    exp = Decimal(10) ** -places
    return value.quantize(exp, rounding=ROUND_HALF_UP)


def safe_divide(
    numerator: Decimal,
    denominator: Decimal,
    default: Decimal = Decimal("0"),
) -> Decimal:
    """Return numerator / denominator, or *default* when denominator is zero."""
    if denominator == Decimal("0"):
        return default
    return numerator / denominator
