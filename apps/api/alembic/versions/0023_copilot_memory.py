"""Add session_context to copilot_sessions for conversation memory

Revision ID: 0023
Revises: 0022
Create Date: 2026-07-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0023"
down_revision: str | None = "0022"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "copilot_sessions",
        sa.Column("session_context", sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("copilot_sessions", "session_context")
