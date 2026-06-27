"""Reasoning runs: audit trail for LLM invocations

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "reasoning_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "snapshot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("snapshots.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("module_type", sa.String(30), nullable=False),
        sa.Column(
            "compute_run_ids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("prompt_hash", sa.String(64), nullable=False),
        sa.Column("model_version", sa.String(100), nullable=False),
        sa.Column("tokens_in", sa.Integer, nullable=False),
        sa.Column("tokens_out", sa.Integer, nullable=False),
        sa.Column("output_text", sa.Text, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("review_required", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("reviewer_id", sa.String(200), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_outcome", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_reasoning_runs_snapshot_id", "reasoning_runs", ["snapshot_id"])
    op.create_index("ix_reasoning_runs_module_type", "reasoning_runs", ["module_type"])
    op.create_index(
        "ix_reasoning_runs_review_required",
        "reasoning_runs",
        ["review_required"],
    )


def downgrade() -> None:
    op.drop_table("reasoning_runs")
