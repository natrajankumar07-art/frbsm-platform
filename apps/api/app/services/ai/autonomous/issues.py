"""
Autonomous Issues Tracker (Epic 6).

Manages outstanding regulatory and operational issues with
status lifecycle: open → monitoring → resolved.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db.models.autonomous import AutonomousIssueModel


async def create_issue(
    db: AsyncSession,
    title: str,
    description: str,
    category: str = "regulatory",
    severity: str = "warning",
    entity_id: str | None = None,
    context: dict | None = None,
) -> AutonomousIssueModel:
    """Create a new outstanding issue."""
    issue = AutonomousIssueModel(
        id=uuid.uuid4(),
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
        entity_id=uuid.UUID(entity_id) if entity_id else None,
        title=title,
        description=description,
        category=category,
        severity=severity,
        status="open",
        context_json=json.dumps(context or {}),
    )
    db.add(issue)
    await db.flush()
    return issue


async def update_issue_status(
    db: AsyncSession,
    issue_id: str,
    status: str,
) -> AutonomousIssueModel | None:
    """Update the status of an existing issue."""
    issue = await db.get(AutonomousIssueModel, uuid.UUID(issue_id))
    if not issue:
        return None

    valid_statuses = {"open", "monitoring", "resolved"}
    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")

    issue.status = status
    issue.updated_at = datetime.now(tz=timezone.utc)
    if status == "resolved":
        issue.resolved_at = datetime.now(tz=timezone.utc)

    await db.flush()
    return issue


async def list_issues(
    db: AsyncSession,
    status: str | None = None,
    entity_id: str | None = None,
    limit: int = 50,
) -> list[AutonomousIssueModel]:
    """List issues, optionally filtered by status and entity."""
    q = select(AutonomousIssueModel).order_by(AutonomousIssueModel.created_at.desc())

    if status:
        q = q.where(AutonomousIssueModel.status == status)
    if entity_id:
        q = q.where(AutonomousIssueModel.entity_id == uuid.UUID(entity_id))

    result = await db.execute(q.limit(limit))
    return list(result.scalars().all())
