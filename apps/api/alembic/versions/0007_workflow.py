"""Workflow: workpapers, sign-offs, close calendar tasks

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "workpapers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "snapshot_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("snapshots.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("return_code", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("preparer_id", sa.String(200), nullable=True),
        sa.Column("prepared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewer_id", sa.String(200), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approver_id", sa.String(200), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_workpapers_snapshot_id", "workpapers", ["snapshot_id"])
    op.create_index("ix_workpapers_status", "workpapers", ["status"])

    op.create_table(
        "sign_offs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workpaper_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workpapers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("user_id", sa.String(200), nullable=False),
        sa.Column("user_role", sa.String(20), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
    )
    op.create_index("ix_sign_offs_workpaper_id", "sign_offs", ["workpaper_id"])
    op.create_index("ix_sign_offs_user_id", "sign_offs", ["user_id"])

    op.create_table(
        "close_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("period", sa.String(20), nullable=False),
        sa.Column("period_type", sa.String(10), nullable=False),
        sa.Column("task_name", sa.String(200), nullable=False),
        sa.Column("owner_role", sa.String(20), nullable=False),
        sa.Column("owner_user_id", sa.String(200), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("depends_on", sa.Text, nullable=False, server_default="[]"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("sequence_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_close_tasks_period", "close_tasks", ["period"])
    op.create_index("ix_close_tasks_status", "close_tasks", ["status"])


def downgrade() -> None:
    op.drop_table("close_tasks")
    op.drop_table("sign_offs")
    op.drop_table("workpapers")
