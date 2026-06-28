from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CashflowCreate(BaseModel):
    position_id: uuid.UUID
    position_reporting_date: date
    snapshot_id: uuid.UUID
    cashflow_type: str = Field(max_length=30)
    cashflow_date: date
    amount: Decimal
    currency: str = Field(max_length=3)
    is_contractual: bool = True
    time_bucket: str | None = Field(None, max_length=20)


class CashflowUpdate(BaseModel):
    cashflow_type: str | None = Field(None, max_length=30)
    cashflow_date: date | None = None
    amount: Decimal | None = None
    currency: str | None = Field(None, max_length=3)
    is_contractual: bool | None = None
    time_bucket: str | None = Field(None, max_length=20)


class CashflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    position_id: uuid.UUID
    position_reporting_date: date
    snapshot_id: uuid.UUID
    cashflow_type: str
    cashflow_date: date
    amount: Decimal
    currency: str
    is_contractual: bool
    time_bucket: str | None
    created_at: datetime
    updated_at: datetime
