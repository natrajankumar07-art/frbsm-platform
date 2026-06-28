"""Legal entities and capital requirements tables

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RATE = sa.Numeric(precision=10, scale=6)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "legal_entities",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("lei", sa.String(20), nullable=True, unique=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("jurisdiction", sa.String(10), nullable=False),
        sa.Column("regulator", sa.String(50), nullable=False),
        sa.Column("license_type", sa.String(100), nullable=True),
        sa.Column("is_consolidated", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_reporting_entity", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("parent_entity_id", UUID, nullable=True),
        sa.Column("functional_currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_legal_entities_code", "legal_entities", ["code"], unique=True)
    op.create_index("ix_legal_entities_jurisdiction", "legal_entities", ["jurisdiction"])
    op.create_index("ix_legal_entities_entity_type", "legal_entities", ["entity_type"])
    op.create_index(
        "ix_legal_entities_parent_entity_id", "legal_entities", ["parent_entity_id"]
    )

    op.create_table(
        "entity_capital_requirements",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("entity_id", UUID, nullable=False),
        sa.Column("requirement_type", sa.String(50), nullable=False),
        sa.Column("minimum_ratio", RATE, nullable=False),
        sa.Column("buffer_requirement", RATE, nullable=False, server_default="0"),
        sa.Column("effective_from", sa.Date, nullable=False),
        sa.Column("regulatory_reference", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_ecr_entity_type", "entity_capital_requirements", ["entity_id", "requirement_type"]
    )
    op.create_index(
        "ix_ecr_effective_from", "entity_capital_requirements", ["effective_from"]
    )


def downgrade() -> None:
    op.drop_table("entity_capital_requirements")
    op.drop_table("legal_entities")
