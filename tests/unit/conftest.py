"""Unit test fixtures — no I/O, no database, no network."""
from __future__ import annotations

from decimal import Decimal
from datetime import date

import pytest

from domain.enums import (
    AssetClass,
    CurrencyCode,
    Jurisdiction,
    PositionStatus,
    IFRS9Stage,
    RatingGrade,
)
from domain.position import Position


@pytest.fixture
def minimal_position() -> Position:
    """Smallest valid Position with all required fields; optional fields omitted."""
    return Position(
        position_id="POS-001",
        asset_class=AssetClass.CORPORATE_LOAN,
        counterparty_id="CTY-001",
        jurisdiction=Jurisdiction.IN,
        currency=CurrencyCode.INR,
        notional=Decimal("1000000.00"),
        carrying_value=Decimal("950000.00"),
        reporting_date=date(2024, 3, 31),
        origination_date=date(2022, 1, 1),
        maturity_date=date(2027, 1, 1),
        status=PositionStatus.ACTIVE,
        ifrs9_stage=IFRS9Stage.STAGE_1,
        rating_grade=RatingGrade.BBB,
        pd_one_year=Decimal("0.005"),
        lgd=Decimal("0.45"),
        ead=Decimal("1000000.00"),
        is_collateralised=False,
        is_off_balance_sheet=False,
    )
