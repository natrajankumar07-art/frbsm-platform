"""ORM models for Autonomous Banking Intelligence (Epic 6)."""

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AutonomousAlertModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "autonomous_alerts"

    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("legal_entities.id", ondelete="SET NULL"),
        nullable=True,
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metric_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    snapshot_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_autonomous_alerts_entity_id", "entity_id"),
        Index("ix_autonomous_alerts_severity", "severity"),
        Index("ix_autonomous_alerts_status", "status"),
        Index("ix_autonomous_alerts_created_at", "created_at"),
    )


class AutonomousRecommendationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "autonomous_recommendations"

    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("legal_entities.id", ondelete="SET NULL"),
        nullable=True,
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expected_benefit: Mapped[str | None] = mapped_column(Text, nullable=True)
    potential_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    implemented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_autonomous_rec_entity_id", "entity_id"),
        Index("ix_autonomous_rec_status", "status"),
        Index("ix_autonomous_rec_priority", "priority"),
    )


class AutonomousIssueModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "autonomous_issues"

    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("legal_entities.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="warning")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    context_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_autonomous_issues_entity_id", "entity_id"),
        Index("ix_autonomous_issues_status", "status"),
    )


class AutonomousBriefingModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "autonomous_briefings"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("legal_entities.id", ondelete="SET NULL"),
        nullable=True,
    )
    briefing_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    key_metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="generated")
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_autonomous_briefings_entity_id", "entity_id"),
        Index("ix_autonomous_briefings_type", "briefing_type"),
        Index("ix_autonomous_briefings_created_at", "created_at"),
    )


class ScheduledReportConfigModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scheduled_report_configs"

    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("legal_entities.id", ondelete="SET NULL"),
        nullable=True,
    )
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(20), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_run: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(200), nullable=False, default="system")

    __table_args__ = (
        Index("ix_scheduled_reports_entity_id", "entity_id"),
        Index("ix_scheduled_reports_enabled", "enabled"),
    )


class AutonomousMonitoringRunModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "autonomous_monitoring_runs"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("legal_entities.id", ondelete="SET NULL"),
        nullable=True,
    )
    alerts_generated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommendations_generated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    issues_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_monitoring_runs_created_at", "created_at"),
    )
