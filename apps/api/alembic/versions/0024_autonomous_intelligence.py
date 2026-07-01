"""Autonomous banking intelligence tables (Epic 6)

Adds six tables to support persistent monitoring, recommendations,
briefings, issues tracking, scheduled reports, and run history.

Revision ID: 0024
Revises: 0023
Create Date: 2026-07-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0024"
down_revision: str | None = "0023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── autonomous_alerts ──────────────────────────────────────────────────
    op.create_table(
        "autonomous_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legal_entities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),  # info/notice/warning/critical
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=True),
        sa.Column("metric_value", sa.Float, nullable=True),
        sa.Column("threshold_value", sa.Float, nullable=True),
        sa.Column("snapshot_date", sa.Date, nullable=True),
        sa.Column("recommendation", sa.Text, nullable=True),
        sa.Column("evidence_json", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_autonomous_alerts_entity_id", "autonomous_alerts", ["entity_id"])
    op.create_index("ix_autonomous_alerts_severity", "autonomous_alerts", ["severity"])
    op.create_index("ix_autonomous_alerts_status", "autonomous_alerts", ["status"])
    op.create_index("ix_autonomous_alerts_created_at", "autonomous_alerts", ["created_at"])

    # ── autonomous_recommendations ─────────────────────────────────────────
    op.create_table(
        "autonomous_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legal_entities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("priority", sa.Integer, nullable=False, server_default="3"),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("expected_benefit", sa.Text, nullable=True),
        sa.Column("potential_impact", sa.Text, nullable=True),
        sa.Column("evidence_json", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("implemented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_autonomous_rec_entity_id", "autonomous_recommendations", ["entity_id"])
    op.create_index("ix_autonomous_rec_status", "autonomous_recommendations", ["status"])
    op.create_index("ix_autonomous_rec_priority", "autonomous_recommendations", ["priority"])

    # ── autonomous_issues ──────────────────────────────────────────────────
    op.create_table(
        "autonomous_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legal_entities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False, server_default="warning"),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("context_json", sa.Text, nullable=True),
    )
    op.create_index("ix_autonomous_issues_entity_id", "autonomous_issues", ["entity_id"])
    op.create_index("ix_autonomous_issues_status", "autonomous_issues", ["status"])

    # ── autonomous_briefings ───────────────────────────────────────────────
    op.create_table(
        "autonomous_briefings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legal_entities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("briefing_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("key_metrics_json", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="generated"),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_autonomous_briefings_entity_id", "autonomous_briefings", ["entity_id"])
    op.create_index("ix_autonomous_briefings_type", "autonomous_briefings", ["briefing_type"])
    op.create_index("ix_autonomous_briefings_created_at", "autonomous_briefings", ["created_at"])

    # ── scheduled_report_configs ───────────────────────────────────────────
    op.create_table(
        "scheduled_report_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legal_entities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("report_type", sa.String(100), nullable=False),
        sa.Column("schedule_type", sa.String(20), nullable=False),  # daily/weekly/monthly
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("last_run", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(200), nullable=False, server_default="system"),
    )
    op.create_index("ix_scheduled_reports_entity_id", "scheduled_report_configs", ["entity_id"])
    op.create_index("ix_scheduled_reports_enabled", "scheduled_report_configs", ["enabled"])

    # ── autonomous_monitoring_runs ─────────────────────────────────────────
    op.create_table(
        "autonomous_monitoring_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("legal_entities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("alerts_generated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("recommendations_generated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("issues_created", sa.Integer, nullable=False, server_default="0"),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="completed"),
        sa.Column("error_message", sa.Text, nullable=True),
    )
    op.create_index("ix_monitoring_runs_created_at", "autonomous_monitoring_runs", ["created_at"])


def downgrade() -> None:
    op.drop_table("autonomous_monitoring_runs")
    op.drop_table("scheduled_report_configs")
    op.drop_table("autonomous_briefings")
    op.drop_table("autonomous_issues")
    op.drop_table("autonomous_recommendations")
    op.drop_table("autonomous_alerts")
