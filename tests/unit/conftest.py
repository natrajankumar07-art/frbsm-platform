"""Unit test fixtures — no I/O, no database, no network."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest

from domain.enums import (
    AssetClass,
    CurrencyCode,
    HQLALevel,
    IFRS9Stage,
    PositionStatus,
    RatingGrade,
)
from domain.position import Position


@pytest.fixture
def minimal_position() -> Position:
    """Smallest valid Position with all required fields; optional fields omitted."""
    return Position(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        counterparty_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        product_code="CORP-LOAN-001",
        asset_class=AssetClass.CORPORATE,
        currency=CurrencyCode.INR,
        notional=Decimal("1000000.00"),
        booked_amount=Decimal("950000.00"),
        fair_value=Decimal("950000.00"),
        reporting_date=date(2024, 3, 31),
        maturity_date=date(2027, 1, 1),
        status=PositionStatus.ACTIVE,
        ifrs9_stage=IFRS9Stage.STAGE_1,
        credit_grade=RatingGrade.BBB,
        hqla_level=HQLALevel.INELIGIBLE,
    )
