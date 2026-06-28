"""Make stress_test_runs.compute_run_id nullable

Revision ID: 0021
Revises: 0020
Create Date: 2026-06-28

compute_run_id is NOT NULL in 0017 but the compute engine (Epic 3+) does not
exist yet. Making it nullable allows stress test runs to be created through the
API before compute workers are built.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0021"
down_revision: str | None = "0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "stress_test_runs",
        "compute_run_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )


def downgrade() -> None:
    # Set a placeholder before re-adding NOT NULL constraint
    op.execute(
        "UPDATE stress_test_runs SET compute_run_id = gen_random_uuid() "
        "WHERE compute_run_id IS NULL"
    )
    op.alter_column(
        "stress_test_runs",
        "compute_run_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
