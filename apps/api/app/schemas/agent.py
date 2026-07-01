"""
Pydantic schemas for the SAM Agent API (Epic 4D).
"""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    user_message: str = Field(..., min_length=1, max_length=4000)
    session_id: uuid.UUID | None = None
    entity_id: uuid.UUID | None = None
    snapshot_id: uuid.UUID | None = None


class PlanRequest(BaseModel):
    user_message: str = Field(..., min_length=1)
    entity_id: uuid.UUID | None = None
    snapshot_id: uuid.UUID | None = None


class StepResponse(BaseModel):
    step_id: str
    tool_name: str
    description: str
    status: str
    start_time: str | None = None
    end_time: str | None = None
    duration_ms: int | None = None
    retry_count: int = 0
    error: str | None = None
    evidence: dict[str, Any] | None = None


class PlanResponse(BaseModel):
    plan_id: str
    intent: str
    status: str
    entity_id: str | None = None
    snapshot_id: str | None = None
    entity_name: str | None = None
    snapshot_date: str | None = None
    created_at: str
    completed_at: str | None = None
    steps: list[StepResponse]
    steps_total: int
    steps_completed: int
    steps_failed: int
    steps_skipped: int


class StepRecordResponse(BaseModel):
    step_id: str
    tool_name: str
    description: str
    status: str
    start_time: str | None = None
    end_time: str | None = None
    duration_ms: int | None = None
    retry_count: int = 0
    error: str | None = None
    evidence_confidence: str = "N/A"


class ExecutionRecordResponse(BaseModel):
    execution_id: str
    plan_id: str
    intent: str
    entity_id: str | None = None
    snapshot_id: str | None = None
    status: str
    steps: list[StepRecordResponse]
    started_at: str
    completed_at: str | None = None
    total_duration_ms: int | None = None
    steps_completed: int
    steps_failed: int
    steps_skipped: int


class ExecutionHistoryResponse(BaseModel):
    executions: list[ExecutionRecordResponse]
    total: int


class AlertResponse(BaseModel):
    alert_id: str
    severity: str
    category: str
    title: str
    message: str
    entity: str
    snapshot_date: str
    metric_name: str = ""
    metric_value: float | None = None
    threshold: float | None = None
    generated_at: str


class AlertsResponse(BaseModel):
    alerts: list[AlertResponse]
    total: int
    critical: int
    high: int
    medium: int


class TimelineEventResponse(BaseModel):
    stage: str
    label: str
    detail: str
    timestamp: str
    status: str


class TimelineResponse(BaseModel):
    plan_id: str
    events: list[TimelineEventResponse]


class IntentAnalysisResponse(BaseModel):
    primary_intent: str
    domains: list[str]
    required_tools: list[str]
    time_reference: str | None = None
    entity_reference: str | None = None
    repeat_reference: str | None = None
    report_type_hint: str | None = None
    confidence: float
