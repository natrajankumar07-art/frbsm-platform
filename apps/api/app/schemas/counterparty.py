from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CounterpartyCreate(BaseModel):
    name: str = Field(max_length=500)
    lei: str | None = Field(None, max_length=20)
    sector: str = Field(max_length=100)
    industry: str | None = Field(None, max_length=100)
    geography: str = Field(max_length=2)
    jurisdiction: str = Field(max_length=10)
    group_id: uuid.UUID | None = None
    group_name: str | None = Field(None, max_length=500)
    rating: str = Field(default="UNRATED", max_length=10)
    is_financial_institution: bool = False
    is_sovereign: bool = False
    is_large_exposure: bool = False


class CounterpartyUpdate(BaseModel):
    name: str | None = Field(None, max_length=500)
    lei: str | None = Field(None, max_length=20)
    sector: str | None = Field(None, max_length=100)
    industry: str | None = Field(None, max_length=100)
    geography: str | None = Field(None, max_length=2)
    jurisdiction: str | None = Field(None, max_length=10)
    group_id: uuid.UUID | None = None
    group_name: str | None = Field(None, max_length=500)
    rating: str | None = Field(None, max_length=10)
    is_financial_institution: bool | None = None
    is_sovereign: bool | None = None
    is_large_exposure: bool | None = None


class CounterpartyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    lei: str | None
    sector: str
    industry: str | None
    geography: str
    jurisdiction: str
    group_id: uuid.UUID | None
    group_name: str | None
    rating: str
    is_financial_institution: bool
    is_sovereign: bool
    is_large_exposure: bool
    created_at: datetime
    updated_at: datetime
