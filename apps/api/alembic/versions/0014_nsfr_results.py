"""NSFR (Net Stable Funding Ratio) result tables

Revision ID: 0014
Revises: 0013
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0014"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(precision=28, scale=8)
RATE = sa.Numeric(precision=10, scale=6)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "nsfr_results",
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
        sa.Column("available_stable_funding", MONEY, nullable=False),
        sa.Column("required_stable_funding", MONEY, nullable=False),
        sa.Column("nsfr_ratio", RATE, nullable=False),
        sa.Column("minimum_ratio", RATE, nullable=False, server_default="1.0"),
        sa.Column("passes", sa.Boolean, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_nsfr_snapshot_entity", "nsfr_results", ["snapshot_id", "entity_id"])
    op.create_index("ix_nsfr_compute_run", "nsfr_results", ["compute_run_id"])
    op.create_index("ix_nsfr_passes", "nsfr_results", ["passes"])
    op.execute("""
        ALTER TABLE nsfr_results
        ADD CONSTRAINT uq_nsfr_snapshot_entity UNIQUE (snapshot_id, entity_id)
    """)

    op.create_table(
        "nsfr_asf_components",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "nsfr_result_id",
            UUID,
            sa.ForeignKey("nsfr_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("funding_category", sa.String(100), nullable=False),
        sa.Column("remaining_maturity_bucket", sa.String(30), nullable=False),
        sa.Column("gross_amount", MONEY, nullable=False),
        sa.Column("asf_factor", RATE, nullable=False),
        sa.Column("weighted_amount", MONEY, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_nsfr_asf_result_id", "nsfr_asf_components", ["nsfr_result_id"])
    op.create_index("ix_nsfr_asf_category", "nsfr_asf_components", ["funding_category"])

    op.create_table(
        "nsfr_rsf_components",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "nsfr_result_id",
            UUID,
            sa.ForeignKey("nsfr_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("asset_category", sa.String(100), nullable=False),
        sa.Column("remaining_maturity_bucket", sa.String(30), nullable=False),
        sa.Column("gross_amount", MONEY, nullable=False),
        sa.Column("rsf_factor", RATE, nullable=False),
        sa.Column("weighted_amount", MONEY, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_nsfr_rsf_result_id", "nsfr_rsf_components", ["nsfr_result_id"])
    op.create_index("ix_nsfr_rsf_category", "nsfr_rsf_components", ["asset_category"])


def downgrade() -> None:
    op.drop_table("nsfr_rsf_components")
    op.drop_table("nsfr_asf_components")
    op.drop_table("nsfr_results")
