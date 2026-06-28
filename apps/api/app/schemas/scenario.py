from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ScenarioCreate(BaseModel):
    code: str = Field(max_length=50)
    name: str = Field(max_length=200)
    description: str | None = None
    scenario_type: str = Field(max_length=30)
    severity: str | None = Field(None, max_length=20)
    is_regulatory: bool = False
    regulatory_reference: str | None = Field(None, max_length=200)
    is_active: bool = True
    created_by: str = Field(max_length=200)


class ScenarioUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    scenario_type: str | None = Field(None, max_length=30)
    severity: str | None = Field(None, max_length=20)
    is_regulatory: bool | None = None
    regulatory_reference: str | None = Field(None, max_length=200)
    is_active: bool | None = None


class ScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    description: str | None
    scenario_type: str
    severity: str | None
    is_regulatory: bool
    regulatory_reference: str | None
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


class ScenarioParameterCreate(BaseModel):
    parameter_type: str = Field(max_length=50)
    parameter_name: str = Field(max_length=100)
    shock_type: str = Field(max_length=30)
    shock_value: Decimal
    asset_class: str | None = Field(None, max_length=50)
    jurisdiction: str | None = Field(None, max_length=10)
    currency: str | None = Field(None, max_length=3)
    time_horizon_days: int | None = None


class ScenarioParameterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scenario_id: uuid.UUID
    parameter_type: str
    parameter_name: str
    shock_type: str
    shock_value: Decimal
    asset_class: str | None
    jurisdiction: str | None
    currency: str | None
    time_horizon_days: int | None
    created_at: datetime
    updated_at: datetime
