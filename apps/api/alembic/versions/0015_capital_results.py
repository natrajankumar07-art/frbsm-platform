"""Capital adequacy result table — CET1, Tier 1, Total Capital, RWA, ratios

Revision ID: 0015
Revises: 0014
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0015"
down_revision: str | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(precision=28, scale=8)
RATE = sa.Numeric(precision=10, scale=6)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "capital_results",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "snapshot_id",
            UUID,
            sa.ForeignKey("snapshots.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("entity_id", UUID, nullable=False),
        sa.Column(
            "compute_run_id",
            UUID,
            sa.ForeignKey("compute_runs.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        # Capital components (Basel III CRE20)
        sa.Column("cet1_capital", MONEY, nullable=False),
        sa.Column("additional_tier1", MONEY, nullable=False),
        sa.Column("tier2_capital", MONEY, nullable=False),
        sa.Column("total_capital", MONEY, nullable=False),
        # RWA by risk type
        sa.Column("rwa_credit", MONEY, nullable=False),
        sa.Column("rwa_market", MONEY, nullable=False),
        sa.Column("rwa_operational", MONEY, nullable=False),
        sa.Column("total_rwa", MONEY, nullable=False),
        # Capital ratios
        sa.Column("cet1_ratio", RATE, nullable=False),
        sa.Column("tier1_ratio", RATE, nullable=False),
        sa.Column("total_capital_ratio", RATE, nullable=False),
        sa.Column("leverage_ratio", RATE, nullable=False),
        # Regulatory thresholds effective at snapshot date
        sa.Column("cet1_minimum", RATE, nullable=False, server_default="0.045"),
        sa.Column("tier1_minimum", RATE, nullable=False, server_default="0.06"),
        sa.Column("total_minimum", RATE, nullable=False, server_default="0.08"),
        sa.Column("passes_all", sa.Boolean, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_capital_snapshot_entity", "capital_results", ["snapshot_id", "entity_id"]
    )
    op.create_index("ix_capital_compute_run", "capital_results", ["compute_run_id"])
    op.create_index("ix_capital_passes_all", "capital_results", ["passes_all"])
    op.execute("""
        ALTER TABLE capital_results
        ADD CONSTRAINT uq_capital_snapshot_entity UNIQUE (snapshot_id, entity_id)
    """)


def downgrade() -> None:
    op.drop_table("capital_results")
