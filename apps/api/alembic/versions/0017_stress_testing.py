"""Stress testing: runs, results, and position-level impacts

Revision ID: 0017
Revises: 0016
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0017"
down_revision: str | None = "0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(precision=28, scale=8)
RATE = sa.Numeric(precision=20, scale=8)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "stress_test_runs",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "snapshot_id",
            UUID,
            sa.ForeignKey("snapshots.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "scenario_id",
            UUID,
            sa.ForeignKey("scenarios.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "compute_run_id",
            UUID,
            sa.ForeignKey("compute_runs.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("run_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_stress_runs_snapshot_id", "stress_test_runs", ["snapshot_id"])
    op.create_index("ix_stress_runs_scenario_id", "stress_test_runs", ["scenario_id"])
    op.create_index("ix_stress_runs_status", "stress_test_runs", ["status"])

    op.create_table(
        "stress_test_results",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "stress_run_id",
            UUID,
            sa.ForeignKey("stress_test_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entity_id", UUID, nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("baseline_value", RATE, nullable=False),
        sa.Column("stressed_value", RATE, nullable=False),
        sa.Column("absolute_change", RATE, nullable=False),
        sa.Column("percentage_change", RATE, nullable=False),
        sa.Column("threshold_value", RATE, nullable=True),
        sa.Column("breaches_threshold", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_stress_results_run_id", "stress_test_results", ["stress_run_id"])
    op.create_index(
        "ix_stress_results_entity_metric",
        "stress_test_results",
        ["entity_id", "metric_name"],
    )
    op.create_index(
        "ix_stress_results_breaches", "stress_test_results", ["breaches_threshold"]
    )

    op.create_table(
        "stress_position_impacts",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "stress_run_id",
            UUID,
            sa.ForeignKey("stress_test_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position_id", UUID, nullable=False),
        sa.Column("position_reporting_date", sa.Date, nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("baseline_contribution", MONEY, nullable=False),
        sa.Column("stressed_contribution", MONEY, nullable=False),
        sa.Column("impact", MONEY, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_spi_stress_run_id", "stress_position_impacts", ["stress_run_id"])
    op.create_index("ix_spi_position_id", "stress_position_impacts", ["position_id"])
    op.create_index("ix_spi_metric_name", "stress_position_impacts", ["metric_name"])


def downgrade() -> None:
    op.drop_table("stress_position_impacts")
    op.drop_table("stress_test_results")
    op.drop_table("stress_test_runs")
