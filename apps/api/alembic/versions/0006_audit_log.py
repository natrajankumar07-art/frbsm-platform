"""Audit log: append-only, hash-chained tamper-evident record

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-28

DESIGN NOTE: The audit log has no updated_at column by design. It is append-only.
A DDL trigger is created here to enforce this at the database level (belt-and-suspenders
alongside the application-layer enforcement in platform-audit).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.String(200), nullable=False),
        sa.Column("user_role", sa.String(20), nullable=False),
        sa.Column("session_id", sa.String(100), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(200), nullable=True),
        sa.Column("detail", sa.Text, nullable=True),
        sa.Column("request_id", sa.String(100), nullable=True),
        sa.Column("trace_id", sa.String(100), nullable=True),
        sa.Column("entry_hash", sa.String(64), nullable=False),
        sa.Column("prev_hash", sa.String(64), nullable=False),
        sa.Column("sequence_number", sa.Integer, nullable=False),
    )
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])
    op.create_index("ix_audit_log_user_id", "audit_log", ["user_id"])
    op.create_index("ix_audit_log_action", "audit_log", ["action"])
    op.create_index("ix_audit_log_resource", "audit_log", ["resource_type", "resource_id"])
    op.create_index("ix_audit_log_sequence", "audit_log", ["sequence_number"], unique=True)

    # DB-level immutability trigger: reject any UPDATE or DELETE on audit_log
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_log_immutable()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only: UPDATE and DELETE are forbidden';
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_audit_log_immutable
        BEFORE UPDATE OR DELETE ON audit_log
        FOR EACH ROW EXECUTE FUNCTION audit_log_immutable();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_immutable ON audit_log;")
    op.execute("DROP FUNCTION IF EXISTS audit_log_immutable();")
    op.drop_table("audit_log")
