from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Product Groups
# ---------------------------------------------------------------------------


class ProductGroupCreate(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=200)
    parent_group_id: uuid.UUID | None = None
    description: str | None = None


class ProductGroupUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    parent_group_id: uuid.UUID | None = None
    description: str | None = None


class ProductGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    parent_group_id: uuid.UUID | None
    description: str | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------


class ProductCreate(BaseModel):
    code: str = Field(max_length=50)
    name: str = Field(max_length=200)
    product_group_id: uuid.UUID
    asset_class: str = Field(max_length=50)
    instrument_type: str = Field(max_length=50)
    currency: str | None = Field(None, max_length=3)
    basel_asset_class: str | None = Field(None, max_length=50)
    lcr_eligible: bool = False
    nsfr_category: str | None = Field(None, max_length=50)
    ifrs9_scope: bool = True
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    product_group_id: uuid.UUID | None = None
    asset_class: str | None = Field(None, max_length=50)
    instrument_type: str | None = Field(None, max_length=50)
    currency: str | None = Field(None, max_length=3)
    basel_asset_class: str | None = Field(None, max_length=50)
    lcr_eligible: bool | None = None
    nsfr_category: str | None = Field(None, max_length=50)
    ifrs9_scope: bool | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    product_group_id: uuid.UUID
    asset_class: str
    instrument_type: str
    currency: str | None
    basel_asset_class: str | None
    lcr_eligible: bool
    nsfr_category: str | None
    ifrs9_scope: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Behavioral Assumptions
# ---------------------------------------------------------------------------


class BehavioralAssumptionCreate(BaseModel):
    assumption_type: str = Field(max_length=50)
    parameter_name: str = Field(max_length=100)
    parameter_value: Decimal
    effective_from: date
    effective_to: date | None = None
    regulatory_reference: str | None = Field(None, max_length=200)


class BehavioralAssumptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    assumption_type: str
    parameter_name: str
    parameter_value: Decimal
    effective_from: date
    effective_to: date | None
    regulatory_reference: str | None
    created_at: datetime
    updated_at: datetime
