"""Initial schema: counterparties, positions, collateral

Revision ID: 0001
Revises:
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(precision=28, scale=8)


def upgrade() -> None:
    op.create_table(
        "counterparties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("lei", sa.String(20), nullable=True, unique=True),
        sa.Column("sector", sa.String(100), nullable=False),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("geography", sa.String(2), nullable=False),
        sa.Column("jurisdiction", sa.String(10), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("group_name", sa.String(500), nullable=True),
        sa.Column("rating", sa.String(10), nullable=False, server_default="UNRATED"),
        sa.Column("is_financial_institution", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_sovereign", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_large_exposure", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_counterparties_lei", "counterparties", ["lei"], unique=True)
    op.create_index("ix_counterparties_jurisdiction", "counterparties", ["jurisdiction"])
    op.create_index("ix_counterparties_sector", "counterparties", ["sector"])
    op.create_index("ix_counterparties_group_id", "counterparties", ["group_id"])

    op.create_table(
        "positions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "counterparty_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("counterparties.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("product_code", sa.String(50), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("notional", MONEY, nullable=False),
        sa.Column("booked_amount", MONEY, nullable=False),
        sa.Column("fair_value", MONEY, nullable=False),
        sa.Column("accrued_interest", MONEY, nullable=False, server_default="0"),
        sa.Column("maturity_date", sa.Date, nullable=True),
        sa.Column("repricing_date", sa.Date, nullable=True),
        sa.Column("behavioural_maturity", sa.Date, nullable=True),
        sa.Column("asset_class", sa.String(50), nullable=False),
        sa.Column("credit_grade", sa.String(10), nullable=False, server_default="UNRATED"),
        sa.Column("ifrs9_stage", sa.String(10), nullable=False, server_default="stage_1"),
        sa.Column("days_past_due", sa.Integer, nullable=False, server_default="0"),
        sa.Column("hqla_level", sa.String(20), nullable=False, server_default="ineligible"),
        sa.Column("deposit_type", sa.String(60), nullable=True),
        sa.Column("customer_segment", sa.String(30), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("reporting_date", sa.Date, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_positions_counterparty_id", "positions", ["counterparty_id"])
    op.create_index("ix_positions_reporting_date", "positions", ["reporting_date"])
    op.create_index("ix_positions_ifrs9_stage", "positions", ["ifrs9_stage"])
    op.create_index("ix_positions_asset_class", "positions", ["asset_class"])
    op.create_index("ix_positions_status", "positions", ["status"])

    op.create_table(
        "collateral",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "position_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("positions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("collateral_type", sa.String(40), nullable=False),
        sa.Column("description", sa.String(500), nullable=False, server_default=""),
        sa.Column("market_value", MONEY, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("haircut", MONEY, nullable=False, server_default="0"),
        sa.Column("net_value", MONEY, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_collateral_position_id", "collateral", ["position_id"])


def downgrade() -> None:
    op.drop_table("collateral")
    op.drop_table("positions")
    op.drop_table("counterparties")
