"""Pydantic schemas for Autonomous Banking Intelligence API (Epic 6)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator


# ── Alerts ─────────────────────────────────────────────────────────────────

class AlertResponse(BaseModel):
    id: str
    created_at: datetime
    entity_id: str | None
    category: str
    severity: str
    title: str
    message: str
    metric_name: str | None
    metric_value: float | None
    threshold_value: float | None
    snapshot_date: str | None
    recommendation: str | None
    evidence: dict
    status: str
    acknowledged_at: datetime | None
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


class AlertsResponse(BaseModel):
    alerts: list[AlertResponse]
    total: int
    critical_count: int
    warning_count: int
    notice_count: int
    info_count: int


class AlertStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in {"open", "acknowledged", "resolved"}:
            raise ValueError("status must be open, acknowledged, or resolved")
        return v


# ── Recommendations ────────────────────────────────────────────────────────

class RecommendationResponse(BaseModel):
    id: str
    created_at: datetime
    entity_id: str | None
    category: str
    priority: int
    title: str
    description: str
    expected_benefit: str | None
    potential_impact: str | None
    evidence: dict
    status: str
    implemented_at: datetime | None
    dismissed_at: datetime | None

    model_config = {"from_attributes": True}


class RecommendationsResponse(BaseModel):
    recommendations: list[RecommendationResponse]
    total: int


class RecommendationStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in {"active", "implemented", "dismissed"}:
            raise ValueError("status must be active, implemented, or dismissed")
        return v


# ── Issues ─────────────────────────────────────────────────────────────────

class IssueCreateRequest(BaseModel):
    title: str
    description: str
    category: str = "regulatory"
    severity: str = "warning"
    entity_id: str | None = None
    context: dict | None = None

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        if v not in {"info", "notice", "warning", "critical"}:
            raise ValueError("severity must be info, notice, warning, or critical")
        return v


class IssueResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    entity_id: str | None
    title: str
    description: str
    category: str | None
    severity: str
    status: str
    resolved_at: datetime | None
    context: dict

    model_config = {"from_attributes": True}


class IssueStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in {"open", "monitoring", "resolved"}:
            raise ValueError("status must be open, monitoring, or resolved")
        return v


class IssuesResponse(BaseModel):
    issues: list[IssueResponse]
    total: int
    open_count: int
    monitoring_count: int
    resolved_count: int


# ── Briefings ──────────────────────────────────────────────────────────────

class BriefingGenerateRequest(BaseModel):
    briefing_type: str = "morning"
    entity_id: str | None = None

    @field_validator("briefing_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = {"morning", "daily", "weekly", "monthly_board", "quarterly_exec"}
        if v not in valid:
            raise ValueError(f"briefing_type must be one of {valid}")
        return v


class BriefingResponse(BaseModel):
    id: str
    created_at: datetime
    entity_id: str | None
    briefing_type: str
    content: str
    key_metrics: dict
    status: str
    delivered_at: datetime | None

    model_config = {"from_attributes": True}


class BriefingsResponse(BaseModel):
    briefings: list[BriefingResponse]
    total: int


# ── Scheduled Reports ──────────────────────────────────────────────────────

class ScheduledReportCreateRequest(BaseModel):
    report_type: str
    schedule_type: str
    entity_id: str | None = None
    enabled: bool = True

    @field_validator("schedule_type")
    @classmethod
    def validate_schedule(cls, v: str) -> str:
        if v not in {"daily", "weekly", "monthly"}:
            raise ValueError("schedule_type must be daily, weekly, or monthly")
        return v

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        valid = {
            "ceo_brief", "cro_report", "board_pack", "liquidity_risk",
            "capital_adequacy", "icaap", "ilaap", "stress_testing",
            "regulatory_compliance", "executive_dashboard",
        }
        if v not in valid:
            raise ValueError(f"report_type must be one of {valid}")
        return v


class ScheduledReportUpdateRequest(BaseModel):
    enabled: bool | None = None
    schedule_type: str | None = None


class ScheduledReportResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    entity_id: str | None
    report_type: str
    schedule_type: str
    enabled: bool
    last_run: datetime | None
    next_run: datetime | None
    created_by: str

    model_config = {"from_attributes": True}


class ScheduledReportsResponse(BaseModel):
    configs: list[ScheduledReportResponse]
    total: int


# ── Activity Feed ──────────────────────────────────────────────────────────

class ActivityItem(BaseModel):
    id: str
    type: str
    title: str
    detail: str
    severity: str | None
    timestamp: datetime


class ActivityResponse(BaseModel):
    items: list[ActivityItem]
    total: int


# ── Monitoring Status ──────────────────────────────────────────────────────

class MonitoringRunResponse(BaseModel):
    id: str
    created_at: datetime
    alerts_generated: int
    recommendations_generated: int
    issues_created: int
    duration_ms: int | None
    status: str
    error_message: str | None

    model_config = {"from_attributes": True}


class SchedulerStatusResponse(BaseModel):
    running: bool
    interval_seconds: int
    description: str
    last_run: datetime | None = None
