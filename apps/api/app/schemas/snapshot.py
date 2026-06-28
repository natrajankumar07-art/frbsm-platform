from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

_PLACEHOLDER_HASH = "0" * 64


class SnapshotCreate(BaseModel):
    reporting_date: date
    frozen_by: str = Field(max_length=200)
    position_hash: str = Field(default=_PLACEHOLDER_HASH, max_length=64)
    reference_hash: str = Field(default=_PLACEHOLDER_HASH, max_length=64)
    position_count: int = Field(default=0, ge=0)
    notes: str | None = None


class SnapshotUpdate(BaseModel):
    notes: str | None = None
    position_count: int | None = Field(None, ge=0)


class SnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reporting_date: date
    frozen_at: datetime
    frozen_by: str
    position_hash: str
    reference_hash: str
    position_count: int
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
