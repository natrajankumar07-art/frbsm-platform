"""Reference data: risk weights, HQLA haircuts, run-off rates, CCFs, yield curves

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RATE = sa.Numeric(precision=10, scale=6)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "reference_risk_weights",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("asset_class", sa.String(50), nullable=False),
        sa.Column("rating", sa.String(10), nullable=True),
        sa.Column("jurisdiction", sa.String(10), nullable=True),
        sa.Column("risk_weight", RATE, nullable=False),
        sa.Column("effective_from", sa.Date, nullable=False),
        sa.Column("regulatory_reference", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_rw_asset_class_rating",
        "reference_risk_weights",
        ["asset_class", "rating"],
    )
    op.create_index("ix_rw_effective_from", "reference_risk_weights", ["effective_from"])

    op.create_table(
        "reference_hqla_haircuts",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("hqla_level", sa.String(20), nullable=False),
        sa.Column("collateral_type", sa.String(40), nullable=True),
        sa.Column("haircut", RATE, nullable=False),
        sa.Column("effective_from", sa.Date, nullable=False),
        sa.Column("regulatory_reference", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_hqla_level_effective",
        "reference_hqla_haircuts",
        ["hqla_level", "effective_from"],
    )

    op.create_table(
        "reference_run_off_rates",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("deposit_type", sa.String(60), nullable=False),
        sa.Column("customer_segment", sa.String(30), nullable=False),
        sa.Column("run_off_rate", RATE, nullable=False),
        sa.Column("effective_from", sa.Date, nullable=False),
        sa.Column("regulatory_reference", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_run_off_deposit_segment",
        "reference_run_off_rates",
        ["deposit_type", "customer_segment"],
    )

    op.create_table(
        "reference_ccf",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("commitment_type", sa.String(100), nullable=False),
        sa.Column("original_maturity_lt_1y", sa.Boolean, nullable=True),
        sa.Column("ccf", RATE, nullable=False),
        sa.Column("effective_from", sa.Date, nullable=False),
        sa.Column("regulatory_reference", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )

    op.create_table(
        "reference_yield_curves",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("curve_type", sa.String(20), nullable=False),
        sa.Column("tenors_years", postgresql.ARRAY(sa.Numeric(10, 4)), nullable=False),
        sa.Column("rates", postgresql.ARRAY(sa.Numeric(10, 6)), nullable=False),
        sa.Column("as_of_date", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_yield_curve_ccy_type_date",
        "reference_yield_curves",
        ["currency", "curve_type", "as_of_date"],
    )


def downgrade() -> None:
    op.drop_table("reference_yield_curves")
    op.drop_table("reference_ccf")
    op.drop_table("reference_run_off_rates")
    op.drop_table("reference_hqla_haircuts")
    op.drop_table("reference_risk_weights")
