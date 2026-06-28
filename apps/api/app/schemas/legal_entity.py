from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class LegalEntityCreate(BaseModel):
    code: str = Field(max_length=20)
    name: str = Field(max_length=500)
    lei: str | None = Field(None, max_length=20)
    entity_type: str = Field(max_length=50)
    jurisdiction: str = Field(max_length=10)
    regulator: str = Field(max_length=50)
    license_type: str | None = Field(None, max_length=100)
    is_consolidated: bool = True
    is_reporting_entity: bool = False
    parent_entity_id: uuid.UUID | None = None
    functional_currency: str = Field(default="INR", max_length=3)


class LegalEntityUpdate(BaseModel):
    name: str | None = Field(None, max_length=500)
    lei: str | None = Field(None, max_length=20)
    entity_type: str | None = Field(None, max_length=50)
    jurisdiction: str | None = Field(None, max_length=10)
    regulator: str | None = Field(None, max_length=50)
    license_type: str | None = Field(None, max_length=100)
    is_consolidated: bool | None = None
    is_reporting_entity: bool | None = None
    parent_entity_id: uuid.UUID | None = None
    functional_currency: str | None = Field(None, max_length=3)


class LegalEntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    lei: str | None
    entity_type: str
    jurisdiction: str
    regulator: str
    license_type: str | None
    is_consolidated: bool
    is_reporting_entity: bool
    parent_entity_id: uuid.UUID | None
    functional_currency: str
    created_at: datetime
    updated_at: datetime


class CapitalRequirementCreate(BaseModel):
    requirement_type: str = Field(max_length=50)
    minimum_ratio: float = Field(ge=0.0, le=1.0)
    buffer_requirement: float = Field(default=0.0, ge=0.0)
    effective_from: date
    regulatory_reference: str | None = Field(None, max_length=200)


class CapitalRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entity_id: uuid.UUID
    requirement_type: str
    minimum_ratio: float
    buffer_requirement: float
    effective_from: date
    regulatory_reference: str | None
    created_at: datetime
    updated_at: datetime
