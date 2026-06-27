"""Snapshots: point-in-time frozen data for regulatory computation

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("reporting_date", sa.Date, nullable=False),
        sa.Column("frozen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("frozen_by", sa.String(200), nullable=False),
        sa.Column("position_hash", sa.String(64), nullable=False),   # SHA-256 hex
        sa.Column("reference_hash", sa.String(64), nullable=False),  # SHA-256 hex
        sa.Column("position_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(10), nullable=False, server_default="draft"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_snapshots_reporting_date", "snapshots", ["reporting_date"])
    op.create_index("ix_snapshots_status", "snapshots", ["status"])


def downgrade() -> None:
    op.drop_table("snapshots")
