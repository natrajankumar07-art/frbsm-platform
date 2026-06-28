"""Scenario management: scenario definitions and parameter sets

Revision ID: 0016
Revises: 0015
Create Date: 2026-06-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0016"
down_revision: str | None = "0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RATE = sa.Numeric(precision=20, scale=8)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "scenarios",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("scenario_type", sa.String(30), nullable=False),
        sa.Column("severity", sa.String(20), nullable=True),
        sa.Column("is_regulatory", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("regulatory_reference", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_by", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_scenarios_type", "scenarios", ["scenario_type"])
    op.create_index("ix_scenarios_is_regulatory", "scenarios", ["is_regulatory"])
    op.create_index("ix_scenarios_is_active", "scenarios", ["is_active"])

    op.create_table(
        "scenario_parameter_sets",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "scenario_id",
            UUID,
            sa.ForeignKey("scenarios.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("parameter_type", sa.String(50), nullable=False),
        sa.Column("parameter_name", sa.String(100), nullable=False),
        sa.Column("shock_type", sa.String(30), nullable=False),
        sa.Column("shock_value", RATE, nullable=False),
        sa.Column("asset_class", sa.String(50), nullable=True),
        sa.Column("jurisdiction", sa.String(10), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("time_horizon_days", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_scenario_params_scenario_id", "scenario_parameter_sets", ["scenario_id"]
    )
    op.create_index("ix_scenario_params_type", "scenario_parameter_sets", ["parameter_type"])


def downgrade() -> None:
    op.drop_table("scenario_parameter_sets")
    op.drop_table("scenarios")
