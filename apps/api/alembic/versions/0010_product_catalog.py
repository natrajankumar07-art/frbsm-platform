"""Product catalog: product groups, products, behavioral assumptions

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RATE = sa.Numeric(precision=10, scale=6)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "product_groups",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("parent_group_id", UUID, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_product_groups_code", "product_groups", ["code"], unique=True)
    op.create_index("ix_product_groups_parent", "product_groups", ["parent_group_id"])

    op.create_table(
        "products",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "product_group_id",
            UUID,
            sa.ForeignKey("product_groups.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("asset_class", sa.String(50), nullable=False),
        sa.Column("instrument_type", sa.String(50), nullable=False),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("basel_asset_class", sa.String(50), nullable=True),
        sa.Column("lcr_eligible", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("nsfr_category", sa.String(50), nullable=True),
        sa.Column("ifrs9_scope", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_products_code", "products", ["code"], unique=True)
    op.create_index("ix_products_product_group_id", "products", ["product_group_id"])
    op.create_index("ix_products_asset_class", "products", ["asset_class"])
    op.create_index("ix_products_instrument_type", "products", ["instrument_type"])

    op.create_table(
        "product_behavioral_assumptions",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "product_id",
            UUID,
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("assumption_type", sa.String(50), nullable=False),
        sa.Column("parameter_name", sa.String(100), nullable=False),
        sa.Column("parameter_value", RATE, nullable=False),
        sa.Column("effective_from", sa.Date, nullable=False),
        sa.Column("effective_to", sa.Date, nullable=True),
        sa.Column("regulatory_reference", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_pba_product_id", "product_behavioral_assumptions", ["product_id"])
    op.create_index(
        "ix_pba_assumption_type", "product_behavioral_assumptions", ["assumption_type"]
    )
    op.create_index(
        "ix_pba_effective_from", "product_behavioral_assumptions", ["effective_from"]
    )


def downgrade() -> None:
    op.drop_table("product_behavioral_assumptions")
    op.drop_table("products")
    op.drop_table("product_groups")
