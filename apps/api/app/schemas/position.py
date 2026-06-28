from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PositionCreate(BaseModel):
    reporting_date: date
    counterparty_id: uuid.UUID
    product_code: str = Field(max_length=50)
    currency: str = Field(max_length=3)
    notional: Decimal = Field(ge=Decimal("0"))
    booked_amount: Decimal
    fair_value: Decimal
    accrued_interest: Decimal = Decimal("0")
    maturity_date: date | None = None
    repricing_date: date | None = None
    behavioural_maturity: date | None = None
    asset_class: str = Field(max_length=50)
    credit_grade: str = Field(default="UNRATED", max_length=10)
    ifrs9_stage: str = Field(default="stage_1", max_length=10)
    days_past_due: int = Field(default=0, ge=0)
    hqla_level: str = Field(default="ineligible", max_length=20)
    deposit_type: str | None = Field(None, max_length=60)
    customer_segment: str | None = Field(None, max_length=30)
    status: str = Field(default="active", max_length=20)


class PositionUpdate(BaseModel):
    product_code: str | None = Field(None, max_length=50)
    currency: str | None = Field(None, max_length=3)
    notional: Decimal | None = Field(None, ge=Decimal("0"))
    booked_amount: Decimal | None = None
    fair_value: Decimal | None = None
    accrued_interest: Decimal | None = None
    maturity_date: date | None = None
    repricing_date: date | None = None
    behavioural_maturity: date | None = None
    asset_class: str | None = Field(None, max_length=50)
    credit_grade: str | None = Field(None, max_length=10)
    ifrs9_stage: str | None = Field(None, max_length=10)
    days_past_due: int | None = Field(None, ge=0)
    hqla_level: str | None = Field(None, max_length=20)
    deposit_type: str | None = Field(None, max_length=60)
    customer_segment: str | None = Field(None, max_length=30)
    status: str | None = Field(None, max_length=20)


class PositionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reporting_date: date
    counterparty_id: uuid.UUID
    product_code: str
    currency: str
    notional: Decimal
    booked_amount: Decimal
    fair_value: Decimal
    accrued_interest: Decimal
    maturity_date: date | None
    repricing_date: date | None
    behavioural_maturity: date | None
    asset_class: str
    credit_grade: str
    ifrs9_stage: str
    days_past_due: int
    hqla_level: str
    deposit_type: str | None
    customer_segment: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class CollateralCreate(BaseModel):
    position_reporting_date: date
    collateral_type: str = Field(max_length=40)
    description: str = Field(default="", max_length=500)
    market_value: Decimal = Field(ge=Decimal("0"))
    currency: str = Field(max_length=3)
    haircut: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("1"))
    net_value: Decimal = Field(ge=Decimal("0"))


class CollateralResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    position_id: uuid.UUID
    position_reporting_date: date
    collateral_type: str
    description: str
    market_value: Decimal
    currency: str
    haircut: Decimal
    net_value: Decimal
    created_at: datetime
    updated_at: datetime
