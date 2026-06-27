"""Verify that the database schema is created correctly by ORM model declarations.

Note on trigger tests: the audit_log immutability trigger is created by Alembic
migration 0006, not by SQLAlchemy's create_all. Trigger tests live in
test_audit_log.py and require an Alembic-migrated database (Epic 3+).
"""
from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_core_tables_exist(db_session: AsyncSession) -> None:
    """All expected tables must exist after create_all from ORM models."""
    expected_tables = {
        "counterparties",
        "positions",
        "collateral",
        "snapshots",
        "compute_runs",
        "reasoning_runs",
        "workpapers",
        "sign_offs",
        "close_tasks",
        "audit_log",
    }
    result = await db_session.execute(
        text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public'"
        )
    )
    actual_tables = {row[0] for row in result.fetchall()}
    missing = expected_tables - actual_tables
    assert not missing, f"Missing tables: {missing}"


@pytest.mark.asyncio
async def test_audit_log_has_no_pk_sequence(db_session: AsyncSession) -> None:
    """audit_log uses UUID PK, not a serial sequence — confirming append-only semantics."""
    result = await db_session.execute(
        text(
            "SELECT column_default FROM information_schema.columns "
            "WHERE table_name = 'audit_log' AND column_name = 'id'"
        )
    )
    row = result.fetchone()
    assert row is not None
    # Default should be gen_random_uuid() or similar, not a nextval sequence
    assert row[0] is None or "nextval" not in str(row[0])


@pytest.mark.asyncio
async def test_positions_counterparty_fk_is_restrict(db_session: AsyncSession) -> None:
    """Positions.counterparty_id FK must use RESTRICT (not CASCADE) — prevents data loss."""
    result = await db_session.execute(
        text(
            "SELECT delete_rule FROM information_schema.referential_constraints rc "
            "JOIN information_schema.key_column_usage kcu "
            "  ON rc.constraint_name = kcu.constraint_name "
            "WHERE kcu.table_name = 'positions' "
            "  AND kcu.column_name = 'counterparty_id'"
        )
    )
    row = result.fetchone()
    assert row is not None, "FK constraint not found for positions.counterparty_id"
    assert row[0] == "RESTRICT", (
        f"Expected RESTRICT, got {row[0]}. Deleting a counterparty must not cascade-delete positions."
    )
