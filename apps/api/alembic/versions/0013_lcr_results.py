"""LCR (Liquidity Coverage Ratio) result tables

Revision ID: 0013
Revises: 0012
Create Date: 2026-06-28

LCR computation output tables per Basel III LCR standard (LCR30, LCR40).
All values are Python-computed; never LLM-generated.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(precision=28, scale=8)
RATE = sa.Numeric(precision=10, scale=6)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "lcr_results",
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
        sa.Column("hqla_total", MONEY, nullable=False),
        sa.Column("net_cash_outflows", MONEY, nullable=False),
        sa.Column("total_outflows", MONEY, nullable=False),
        sa.Column("total_inflows", MONEY, nullable=False),
        sa.Column("inflow_cap_applied", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("lcr_ratio", RATE, nullable=False),
        sa.Column("minimum_ratio", RATE, nullable=False, server_default="1.0"),
        sa.Column("passes", sa.Boolean, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_lcr_snapshot_entity", "lcr_results", ["snapshot_id", "entity_id"])
    op.create_index("ix_lcr_compute_run", "lcr_results", ["compute_run_id"])
    op.create_index("ix_lcr_passes", "lcr_results", ["passes"])
    op.execute("""
        ALTER TABLE lcr_results
        ADD CONSTRAINT uq_lcr_snapshot_entity UNIQUE (snapshot_id, entity_id)
    """)

    op.create_table(
        "lcr_hqla_components",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "lcr_result_id",
            UUID,
            sa.ForeignKey("lcr_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("hqla_level", sa.String(20), nullable=False),
        sa.Column("asset_class", sa.String(50), nullable=False),
        sa.Column("gross_amount", MONEY, nullable=False),
        sa.Column("haircut_rate", RATE, nullable=False),
        sa.Column("net_amount", MONEY, nullable=False),
        sa.Column("cap_applies", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_lcr_hqla_result_id", "lcr_hqla_components", ["lcr_result_id"])
    op.create_index("ix_lcr_hqla_level", "lcr_hqla_components", ["hqla_level"])

    op.create_table(
        "lcr_outflow_components",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "lcr_result_id",
            UUID,
            sa.ForeignKey("lcr_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("outflow_category", sa.String(100), nullable=False),
        sa.Column("deposit_type", sa.String(60), nullable=True),
        sa.Column("customer_segment", sa.String(30), nullable=True),
        sa.Column("gross_outflow", MONEY, nullable=False),
        sa.Column("run_off_rate", RATE, nullable=False),
        sa.Column("net_outflow", MONEY, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_lcr_outflow_result_id", "lcr_outflow_components", ["lcr_result_id"])
    op.create_index("ix_lcr_outflow_category", "lcr_outflow_components", ["outflow_category"])

    op.create_table(
        "lcr_inflow_components",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "lcr_result_id",
            UUID,
            sa.ForeignKey("lcr_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("inflow_category", sa.String(100), nullable=False),
        sa.Column("asset_class", sa.String(50), nullable=True),
        sa.Column("gross_inflow", MONEY, nullable=False),
        sa.Column("inflow_rate", RATE, nullable=False, server_default="1.0"),
        sa.Column("net_inflow", MONEY, nullable=False),
        sa.Column("inflow_cap_applies", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_lcr_inflow_result_id", "lcr_inflow_components", ["lcr_result_id"])
    op.create_index("ix_lcr_inflow_category", "lcr_inflow_components", ["inflow_category"])


def downgrade() -> None:
    op.drop_table("lcr_inflow_components")
    op.drop_table("lcr_outflow_components")
    op.drop_table("lcr_hqla_components")
    op.drop_table("lcr_results")
