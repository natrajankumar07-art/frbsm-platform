"""Add copilot_sessions and copilot_messages tables

Revision ID: 0022
Revises: 0021
Create Date: 2026-07-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0022"
down_revision: str | None = "0021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "copilot_sessions",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "entity_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("legal_entities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("user_id", sa.String(200), nullable=False, server_default=""),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_copilot_sessions_entity_id", "copilot_sessions", ["entity_id"])

    op.create_table(
        "copilot_messages",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "session_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("copilot_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column(
            "snapshot_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("snapshots.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "entity_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("legal_entities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("context_json", sa.Text, nullable=True),
        sa.Column("model_version", sa.String(100), nullable=True),
        sa.Column("tokens_in", sa.Integer, nullable=True),
        sa.Column("tokens_out", sa.Integer, nullable=True),
        sa.Column("latency_ms", sa.Float, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_copilot_messages_session_id", "copilot_messages", ["session_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_copilot_messages_session_id", table_name="copilot_messages")
    op.drop_table("copilot_messages")
    op.drop_index("ix_copilot_sessions_entity_id", table_name="copilot_sessions")
    op.drop_table("copilot_sessions")
