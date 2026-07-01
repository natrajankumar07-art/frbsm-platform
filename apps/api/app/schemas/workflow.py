"""Pydantic schemas for Epic 4C workflow and report endpoints."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class WorkflowChatRequest(BaseModel):
    session_id: uuid.UUID
    user_message: str = Field(min_length=1, max_length=8000)
    entity_id: uuid.UUID | None = None
    snapshot_id: uuid.UUID | None = None


class ToolExecuteRequest(BaseModel):
    tool_name: str = Field(min_length=1, max_length=100)
    params: dict = Field(default_factory=dict)
    entity_id: uuid.UUID | None = None
    snapshot_id: uuid.UUID | None = None


class ToolExecuteResponse(BaseModel):
    success: bool
    tool_name: str
    data: dict
    evidence: dict
    markdown: str
    error: str | None = None


class ReportGenerateRequest(BaseModel):
    report_type: str = Field(min_length=1, max_length=100)
    entity_id: uuid.UUID
    snapshot_id: uuid.UUID | None = None


class ReportResponse(BaseModel):
    report_type: str
    title: str
    entity: str
    snapshot_date: str
    generated_at: str
    content_markdown: str
    evidence: dict
    export_hints: dict


class ReportTypeInfo(BaseModel):
    id: str
    name: str
    description: str


class SessionMemoryResponse(BaseModel):
    session_id: uuid.UUID
    active_entity_id: str | None
    active_entity_name: str | None
    active_snapshot_id: str | None
    active_snapshot_date: str | None
    recent_entity_ids: list[str]
    recent_snapshot_ids: list[str]
    report_history: list[dict]
    last_tool_calls: list[dict]


class ToolInfo(BaseModel):
    name: str
    description: str
    input_schema: dict
