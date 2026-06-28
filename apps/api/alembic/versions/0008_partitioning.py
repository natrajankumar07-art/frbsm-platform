"""Convert positions to range-partitioned table by reporting_date

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-28

DESIGN NOTE: positions is the highest-volume table in the platform.
Partitioning by reporting_date (annual range) enables:
  - Partition pruning on every regulatory engine query (all filter by date)
  - Efficient partition-level DROP for old data (7-year retention policy)
  - Parallel query execution across partitions for multi-period analysis

PARTITIONED FK CONSTRAINT NOTE:
PostgreSQL partitioned tables require the partition key in every UNIQUE
constraint. The PRIMARY KEY of the partitioned positions table is
(id, reporting_date). Therefore, collateral's FK references
positions(position_id, position_reporting_date) → positions(id, reporting_date).
The collateral table gains a position_reporting_date column to carry this.

PostgreSQL 16: FKs referencing a partitioned parent table are fully supported
as long as the referenced columns form a unique constraint (including partition key).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MONEY = sa.Numeric(precision=28, scale=8)
UUID = postgresql.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Step 1: Rename existing (unpartitioned) positions table
    # ------------------------------------------------------------------
    op.execute("ALTER TABLE positions RENAME TO positions_legacy")
    op.execute(
        "ALTER INDEX ix_positions_counterparty_id "
        "RENAME TO ix_positions_legacy_counterparty_id"
    )
    op.execute(
        "ALTER INDEX ix_positions_reporting_date "
        "RENAME TO ix_positions_legacy_reporting_date"
    )
    op.execute(
        "ALTER INDEX ix_positions_ifrs9_stage "
        "RENAME TO ix_positions_legacy_ifrs9_stage"
    )
    op.execute(
        "ALTER INDEX ix_positions_asset_class "
        "RENAME TO ix_positions_legacy_asset_class"
    )
    op.execute("ALTER INDEX ix_positions_status RENAME TO ix_positions_legacy_status")

    # Drop FK from collateral (it references the old unpartitioned positions.id)
    op.execute(
        "ALTER TABLE collateral DROP CONSTRAINT IF EXISTS collateral_position_id_fkey"
    )

    # ------------------------------------------------------------------
    # Step 2: Add position_reporting_date to collateral
    #         Required to form the composite FK to the partitioned positions table.
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE collateral
        ADD COLUMN position_reporting_date DATE
    """)

    # Backfill from positions_legacy (empty in fresh setup; handles existing data)
    op.execute("""
        UPDATE collateral c
        SET position_reporting_date = p.reporting_date
        FROM positions_legacy p
        WHERE c.position_id = p.id
    """)

    # For demo seeds that arrive later (all 2026-03-31), set a safe default
    op.execute("""
        UPDATE collateral
        SET position_reporting_date = '2026-03-31'
        WHERE position_reporting_date IS NULL
    """)

    op.execute("""
        ALTER TABLE collateral
        ALTER COLUMN position_reporting_date SET NOT NULL
    """)

    # ------------------------------------------------------------------
    # Step 3: Create the partitioned parent table
    # ------------------------------------------------------------------
    op.execute("""
        CREATE TABLE positions (
            id              UUID            NOT NULL DEFAULT gen_random_uuid(),
            counterparty_id UUID            NOT NULL,
            product_code    VARCHAR(50)     NOT NULL,
            currency        VARCHAR(3)      NOT NULL,
            notional        NUMERIC(28,8)   NOT NULL,
            booked_amount   NUMERIC(28,8)   NOT NULL,
            fair_value      NUMERIC(28,8)   NOT NULL,
            accrued_interest NUMERIC(28,8)  NOT NULL DEFAULT 0,
            maturity_date   DATE,
            repricing_date  DATE,
            behavioural_maturity DATE,
            asset_class     VARCHAR(50)     NOT NULL,
            credit_grade    VARCHAR(10)     NOT NULL DEFAULT 'UNRATED',
            ifrs9_stage     VARCHAR(10)     NOT NULL DEFAULT 'stage_1',
            days_past_due   INTEGER         NOT NULL DEFAULT 0,
            hqla_level      VARCHAR(20)     NOT NULL DEFAULT 'ineligible',
            deposit_type    VARCHAR(60),
            customer_segment VARCHAR(30),
            status          VARCHAR(20)     NOT NULL DEFAULT 'active',
            reporting_date  DATE            NOT NULL,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
            PRIMARY KEY (id, reporting_date),
            CONSTRAINT fk_positions_counterparty
                FOREIGN KEY (counterparty_id)
                REFERENCES counterparties(id)
                ON DELETE RESTRICT
        ) PARTITION BY RANGE (reporting_date)
    """)

    # ------------------------------------------------------------------
    # Step 4: Create annual partitions — 2020 through 2030
    # ------------------------------------------------------------------
    for year in range(2020, 2031):
        op.execute(f"""
            CREATE TABLE positions_{year}
            PARTITION OF positions
            FOR VALUES FROM ('{year}-01-01') TO ('{year + 1}-01-01')
        """)

    # Default partition catches anything outside the explicit ranges
    op.execute("""
        CREATE TABLE positions_default
        PARTITION OF positions DEFAULT
    """)

    # ------------------------------------------------------------------
    # Step 5: Migrate data from legacy table
    # ------------------------------------------------------------------
    op.execute("""
        INSERT INTO positions
        SELECT * FROM positions_legacy
    """)

    # ------------------------------------------------------------------
    # Step 6: Recreate indexes on the parent (inherited by partitions)
    # ------------------------------------------------------------------
    op.create_index("ix_positions_counterparty_id", "positions", ["counterparty_id"])
    op.create_index("ix_positions_reporting_date", "positions", ["reporting_date"])
    op.create_index("ix_positions_ifrs9_stage", "positions", ["ifrs9_stage"])
    op.create_index("ix_positions_asset_class", "positions", ["asset_class"])
    op.create_index("ix_positions_status", "positions", ["status"])

    # ------------------------------------------------------------------
    # Step 7: Recreate composite FK from collateral to partitioned positions
    #         References (id, reporting_date) — the PK of the partitioned table.
    # ------------------------------------------------------------------
    op.execute("""
        ALTER TABLE collateral
        ADD CONSTRAINT collateral_position_fkey
        FOREIGN KEY (position_id, position_reporting_date)
        REFERENCES positions(id, reporting_date)
        ON DELETE CASCADE
    """)

    # ------------------------------------------------------------------
    # Step 8: Drop legacy table
    # ------------------------------------------------------------------
    op.execute("DROP TABLE positions_legacy")

    op.execute("""
        COMMENT ON TABLE positions IS
        'Partitioned by reporting_date (annual). '
        'PK: (id, reporting_date). '
        'FK to positions from child tables must include reporting_date. '
        'Partitions: positions_YYYY + positions_default. '
        'Add new annual partitions before year-end via migration.'
    """)


def downgrade() -> None:
    op.execute(
        "ALTER TABLE collateral DROP CONSTRAINT IF EXISTS collateral_position_fkey"
    )

    op.execute("""
        CREATE TABLE positions_restore (
            id              UUID            NOT NULL DEFAULT gen_random_uuid(),
            counterparty_id UUID            NOT NULL,
            product_code    VARCHAR(50)     NOT NULL,
            currency        VARCHAR(3)      NOT NULL,
            notional        NUMERIC(28,8)   NOT NULL,
            booked_amount   NUMERIC(28,8)   NOT NULL,
            fair_value      NUMERIC(28,8)   NOT NULL,
            accrued_interest NUMERIC(28,8)  NOT NULL DEFAULT 0,
            maturity_date   DATE,
            repricing_date  DATE,
            behavioural_maturity DATE,
            asset_class     VARCHAR(50)     NOT NULL,
            credit_grade    VARCHAR(10)     NOT NULL DEFAULT 'UNRATED',
            ifrs9_stage     VARCHAR(10)     NOT NULL DEFAULT 'stage_1',
            days_past_due   INTEGER         NOT NULL DEFAULT 0,
            hqla_level      VARCHAR(20)     NOT NULL DEFAULT 'ineligible',
            deposit_type    VARCHAR(60),
            customer_segment VARCHAR(30),
            status          VARCHAR(20)     NOT NULL DEFAULT 'active',
            reporting_date  DATE            NOT NULL,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            CONSTRAINT fk_positions_restore_counterparty
                FOREIGN KEY (counterparty_id)
                REFERENCES counterparties(id)
                ON DELETE RESTRICT
        )
    """)

    op.execute("INSERT INTO positions_restore SELECT * FROM positions")
    op.execute("DROP TABLE positions CASCADE")
    op.execute("ALTER TABLE positions_restore RENAME TO positions")

    op.create_index("ix_positions_counterparty_id", "positions", ["counterparty_id"])
    op.create_index("ix_positions_reporting_date", "positions", ["reporting_date"])
    op.create_index("ix_positions_ifrs9_stage", "positions", ["ifrs9_stage"])
    op.create_index("ix_positions_asset_class", "positions", ["asset_class"])
    op.create_index("ix_positions_status", "positions", ["status"])

    op.execute("""
        ALTER TABLE collateral
        ADD CONSTRAINT collateral_position_id_fkey
        FOREIGN KEY (position_id) REFERENCES positions(id)
        ON DELETE CASCADE
    """)
    op.execute("ALTER TABLE collateral DROP COLUMN IF EXISTS position_reporting_date")
