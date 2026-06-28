"""Stress test run and result ORM models."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, TimestampMixin, UUIDPrimaryKeyMixin

MONEY = Numeric(precision=28, scale=8)
RATE = Numeric(precision=20, scale=8)


class StressTestRunModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Execution record for a stress test against a scenario/snapshot."""

    __tablename__ = "stress_test_runs"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("snapshots.id", ondelete="RESTRICT"),
        nullable=False,
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    compute_run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("compute_runs.id", ondelete="RESTRICT"),
        nullable=False,
    )
    run_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_stress_runs_snapshot_id", "snapshot_id"),
        Index("ix_stress_runs_scenario_id", "scenario_id"),
        Index("ix_stress_runs_status", "status"),
    )


class StressTestResultModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Aggregated metric-level result for a stress test run."""

    __tablename__ = "stress_test_results"

    stress_run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("stress_test_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
    )
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    baseline_value: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    stressed_value: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    absolute_change: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    percentage_change: Mapped[Decimal] = mapped_column(RATE, nullable=False)
    threshold_value: Mapped[Decimal | None] = mapped_column(RATE, nullable=True)
    breaches_threshold: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("ix_stress_results_run_id", "stress_run_id"),
        Index("ix_stress_results_entity_metric", "entity_id", "metric_name"),
        Index("ix_stress_results_breaches", "breaches_threshold"),
    )


class StressPositionImpactModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Position-level contribution to stress test metric change."""

    __tablename__ = "stress_position_impacts"

    stress_run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("stress_test_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    position_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    position_reporting_date: Mapped[date] = mapped_column(
        "position_reporting_date", nullable=False
    )
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    baseline_contribution: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    stressed_contribution: Mapped[Decimal] = mapped_column(MONEY, nullable=False)
    impact: Mapped[Decimal] = mapped_column(MONEY, nullable=False)

    __table_args__ = (
        Index("ix_spi_stress_run_id", "stress_run_id"),
        Index("ix_spi_position_id", "position_id"),
        Index("ix_spi_metric_name", "metric_name"),
    )
