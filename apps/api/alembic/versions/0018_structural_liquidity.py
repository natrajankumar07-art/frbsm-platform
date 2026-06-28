"""Structural Liquidity Statement (SLS / RBI DSB-II) table

Revision ID: 0018
Revises: 0017
Create Date: 2026-06-28

SLS = Structural Liquidity Statement per RBI DSB-II format.
Shows maturity profile of assets and liabilities across standardised
time buckets and the resulting net position / cumulative gap.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0018"
down_revision: str | None = "0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(precision=28, scale=8)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "structural_liquidity_buckets",
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
        sa.Column("time_bucket", sa.String(20), nullable=False),
        sa.Column("bucket_order", sa.Integer, nullable=False),
        sa.Column("total_inflows", MONEY, nullable=False, server_default="0"),
        sa.Column("total_outflows", MONEY, nullable=False, server_default="0"),
        sa.Column("net_position", MONEY, nullable=False, server_default="0"),
        sa.Column("cumulative_net", MONEY, nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_slb_snapshot_entity", "structural_liquidity_buckets", ["snapshot_id", "entity_id"]
    )
    op.create_index("ix_slb_time_bucket", "structural_liquidity_buckets", ["time_bucket"])
    op.create_index("ix_slb_bucket_order", "structural_liquidity_buckets", ["bucket_order"])
    op.execute("""
        ALTER TABLE structural_liquidity_buckets
        ADD CONSTRAINT uq_slb_snapshot_entity_bucket
        UNIQUE (snapshot_id, entity_id, time_bucket)
    """)

    op.execute("""
        COMMENT ON TABLE structural_liquidity_buckets IS
        'RBI DSB-II Structural Liquidity Statement. '
        'Time buckets: 0_1d, 1_7d, 7_14d, 14_28d, 28d_3m, 3m_6m, 6m_1y, 1y_3y, 3y_5y, gt_5y'
    """)


def downgrade() -> None:
    op.drop_table("structural_liquidity_buckets")
