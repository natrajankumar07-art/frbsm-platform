"""Regulatory parameter history, filings, and filing lineage

Revision ID: 0019
Revises: 0018
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0019"
down_revision: str | None = "0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(precision=28, scale=8)
RATE = sa.Numeric(precision=20, scale=8)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "regulatory_parameter_history",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("parameter_type", sa.String(50), nullable=False),
        sa.Column("parameter_key", sa.String(200), nullable=False),
        sa.Column("old_value", RATE, nullable=True),
        sa.Column("new_value", RATE, nullable=False),
        sa.Column("effective_from", sa.Date, nullable=False),
        sa.Column("effective_to", sa.Date, nullable=True),
        sa.Column("changed_by", sa.String(200), nullable=False),
        sa.Column("regulatory_reference", sa.String(200), nullable=True),
        sa.Column("jurisdiction", sa.String(10), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_reg_param_hist_type_key",
        "regulatory_parameter_history",
        ["parameter_type", "parameter_key"],
    )
    op.create_index(
        "ix_reg_param_hist_effective", "regulatory_parameter_history", ["effective_from"]
    )
    op.create_index(
        "ix_reg_param_hist_jurisdiction", "regulatory_parameter_history", ["jurisdiction"]
    )

    op.create_table(
        "regulatory_filings",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "snapshot_id",
            UUID,
            sa.ForeignKey("snapshots.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("entity_id", UUID, nullable=False),
        sa.Column("return_type", sa.String(50), nullable=False),
        sa.Column("filing_date", sa.Date, nullable=False),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("filed_by", sa.String(200), nullable=True),
        sa.Column("filed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("filing_reference", sa.String(100), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_reg_filings_snapshot_entity", "regulatory_filings", ["snapshot_id", "entity_id"]
    )
    op.create_index("ix_reg_filings_return_type", "regulatory_filings", ["return_type"])
    op.create_index("ix_reg_filings_period_end", "regulatory_filings", ["period_end"])
    op.create_index("ix_reg_filings_status", "regulatory_filings", ["status"])

    op.create_table(
        "regulatory_filing_lineage",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "filing_id",
            UUID,
            sa.ForeignKey("regulatory_filings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "compute_run_id",
            UUID,
            sa.ForeignKey("compute_runs.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("line_item_code", sa.String(100), nullable=False),
        sa.Column("line_item_description", sa.String(500), nullable=True),
        sa.Column("value", MONEY, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_reg_lineage_filing_id", "regulatory_filing_lineage", ["filing_id"])
    op.create_index(
        "ix_reg_lineage_compute_run_id", "regulatory_filing_lineage", ["compute_run_id"]
    )
    op.create_index(
        "ix_reg_lineage_line_item", "regulatory_filing_lineage", ["line_item_code"]
    )


def downgrade() -> None:
    op.drop_table("regulatory_filing_lineage")
    op.drop_table("regulatory_filings")
    op.drop_table("regulatory_parameter_history")
