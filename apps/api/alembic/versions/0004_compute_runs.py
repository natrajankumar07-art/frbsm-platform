"""Compute runs: audit record for every engine invocation

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "compute_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "snapshot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("snapshots.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("engine", sa.String(50), nullable=False),
        sa.Column("function", sa.String(100), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("git_sha", sa.String(40), nullable=False),
        sa.Column("inputs_hash", sa.String(64), nullable=False),
        sa.Column("outputs_hash", sa.String(64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_ms", sa.Integer, nullable=False),
        sa.Column("success", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_compute_runs_snapshot_id", "compute_runs", ["snapshot_id"])
    op.create_index(
        "ix_compute_runs_engine_snapshot",
        "compute_runs",
        ["engine", "snapshot_id"],
    )
    op.create_index("ix_compute_runs_started_at", "compute_runs", ["started_at"])


def downgrade() -> None:
    op.drop_table("compute_runs")
