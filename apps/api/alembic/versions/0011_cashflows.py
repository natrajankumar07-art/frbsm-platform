"""Cashflows and cashflow projections tables

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-28

DESIGN NOTE: cashflows is partitioned by cashflow_date (annual range)
because individual cashflow rows can number in the billions for a full
bank portfolio. Partition pruning by date is critical for LCR/NSFR
bucket queries that filter by 30-day or 1-year horizons.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(precision=28, scale=8)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Cashflows — partitioned by cashflow_date
    # ------------------------------------------------------------------
    op.execute("""
        CREATE TABLE cashflows (
            id                      UUID            NOT NULL DEFAULT gen_random_uuid(),
            position_id             UUID            NOT NULL,
            position_reporting_date DATE            NOT NULL,
            snapshot_id             UUID            NOT NULL,
            cashflow_type           VARCHAR(30)     NOT NULL,
            cashflow_date           DATE            NOT NULL,
            amount                  NUMERIC(28,8)   NOT NULL,
            currency                VARCHAR(3)      NOT NULL,
            is_contractual          BOOLEAN         NOT NULL DEFAULT true,
            time_bucket             VARCHAR(20),
            created_at              TIMESTAMPTZ     NOT NULL DEFAULT now(),
            updated_at              TIMESTAMPTZ     NOT NULL DEFAULT now(),
            PRIMARY KEY (id, cashflow_date),
            CONSTRAINT fk_cashflows_position
                FOREIGN KEY (position_id, position_reporting_date)
                REFERENCES positions(id, reporting_date)
                ON DELETE CASCADE,
            CONSTRAINT fk_cashflows_snapshot
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
                ON DELETE RESTRICT
        ) PARTITION BY RANGE (cashflow_date)
    """)

    for year in range(2020, 2031):
        op.execute(f"""
            CREATE TABLE cashflows_{year}
            PARTITION OF cashflows
            FOR VALUES FROM ('{year}-01-01') TO ('{year + 1}-01-01')
        """)

    op.execute("""
        CREATE TABLE cashflows_default PARTITION OF cashflows DEFAULT
    """)

    op.create_index("ix_cashflows_position_id", "cashflows", ["position_id"])
    op.create_index("ix_cashflows_snapshot_id", "cashflows", ["snapshot_id"])
    op.create_index("ix_cashflows_date", "cashflows", ["cashflow_date"])
    op.create_index("ix_cashflows_time_bucket", "cashflows", ["time_bucket"])

    op.execute("""
        COMMENT ON TABLE cashflows IS
        'Partitioned by cashflow_date (annual). '
        'Stores contractual and behavioural cashflow schedules per position per snapshot.'
    """)

    # ------------------------------------------------------------------
    # Cashflow projections — aggregated per time bucket (not partitioned)
    # ------------------------------------------------------------------
    op.create_table(
        "cashflow_projections",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("position_id", UUID, nullable=False),
        sa.Column("position_reporting_date", sa.Date, nullable=False),
        sa.Column(
            "snapshot_id",
            UUID,
            sa.ForeignKey("snapshots.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("scenario_id", UUID, nullable=True),
        sa.Column("projection_type", sa.String(30), nullable=False),
        sa.Column("time_bucket", sa.String(20), nullable=False),
        sa.Column("inflow_amount", MONEY, nullable=False, server_default="0"),
        sa.Column("outflow_amount", MONEY, nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index(
        "ix_cf_proj_position_snapshot",
        "cashflow_projections",
        ["position_id", "snapshot_id"],
    )
    op.create_index("ix_cf_proj_scenario_id", "cashflow_projections", ["scenario_id"])
    op.create_index("ix_cf_proj_time_bucket", "cashflow_projections", ["time_bucket"])
    op.create_index("ix_cf_proj_type", "cashflow_projections", ["projection_type"])


def downgrade() -> None:
    op.drop_table("cashflow_projections")
    op.execute("DROP TABLE IF EXISTS cashflows CASCADE")
