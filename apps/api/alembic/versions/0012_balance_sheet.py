"""Balance sheet line items and summaries

Revision ID: 0012
Revises: 0011
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(precision=28, scale=8)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "balance_sheet_line_items",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "snapshot_id",
            UUID,
            sa.ForeignKey("snapshots.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("entity_id", UUID, nullable=False),
        sa.Column("account_code", sa.String(50), nullable=False),
        sa.Column("account_name", sa.String(200), nullable=False),
        sa.Column("line_item_type", sa.String(30), nullable=False),
        sa.Column("product_group_id", UUID, nullable=True),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("amount_local", MONEY, nullable=False),
        sa.Column("amount_reporting", MONEY, nullable=False),
        sa.Column("reporting_currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("level", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_bsli_snapshot_entity", "balance_sheet_line_items", ["snapshot_id", "entity_id"]
    )
    op.create_index("ix_bsli_account_code", "balance_sheet_line_items", ["account_code"])
    op.create_index("ix_bsli_line_item_type", "balance_sheet_line_items", ["line_item_type"])
    op.create_index("ix_bsli_product_group", "balance_sheet_line_items", ["product_group_id"])

    op.create_table(
        "balance_sheet_summaries",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "snapshot_id",
            UUID,
            sa.ForeignKey("snapshots.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("entity_id", UUID, nullable=False),
        sa.Column("total_assets", MONEY, nullable=False),
        sa.Column("total_liabilities", MONEY, nullable=False),
        sa.Column("total_equity", MONEY, nullable=False),
        sa.Column("total_off_balance_sheet", MONEY, nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column(
            "compute_run_id",
            UUID,
            sa.ForeignKey("compute_runs.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_bss_snapshot_entity", "balance_sheet_summaries", ["snapshot_id", "entity_id"]
    )
    op.create_index("ix_bss_compute_run", "balance_sheet_summaries", ["compute_run_id"])
    op.execute("""
        ALTER TABLE balance_sheet_summaries
        ADD CONSTRAINT uq_bs_summary_snapshot_entity
        UNIQUE (snapshot_id, entity_id)
    """)


def downgrade() -> None:
    op.drop_table("balance_sheet_summaries")
    op.drop_table("balance_sheet_line_items")
