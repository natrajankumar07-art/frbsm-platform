from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class StressTestRunCreate(BaseModel):
    snapshot_id: uuid.UUID
    scenario_id: uuid.UUID
    run_type: str = Field(max_length=30)


class StressTestRunUpdate(BaseModel):
    run_type: str | None = Field(None, max_length=30)
    status: str | None = Field(None, max_length=20)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None


class StressTestRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    snapshot_id: uuid.UUID
    scenario_id: uuid.UUID
    compute_run_id: uuid.UUID | None
    run_type: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    created_at: datetime
    updated_at: datetime


class StressTestResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stress_run_id: uuid.UUID
    entity_id: uuid.UUID
    metric_name: str
    baseline_value: Decimal
    stressed_value: Decimal
    absolute_change: Decimal
    percentage_change: Decimal
    threshold_value: Decimal | None
    breaches_threshold: bool
    created_at: datetime
    updated_at: datetime


class StressPositionImpactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stress_run_id: uuid.UUID
    position_id: uuid.UUID
    position_reporting_date: date
    metric_name: str
    baseline_contribution: Decimal
    stressed_contribution: Decimal
    impact: Decimal
    created_at: datetime
    updated_at: datetime
