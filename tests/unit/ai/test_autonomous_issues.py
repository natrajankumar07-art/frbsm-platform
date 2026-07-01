"""
Unit tests for autonomous issues service (Epic 6).
DB-dependent functions (create_issue, update_issue_status, list_issues) are tested
via mocked AsyncSession so no live database is needed.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai.autonomous.issues import (
    create_issue,
    list_issues,
    update_issue_status,
)


def _make_mock_issue(
    issue_id: str | None = None,
    status: str = "open",
    severity: str = "warning",
    category: str = "regulatory",
):
    issue = MagicMock()
    issue.id = uuid.UUID(issue_id) if issue_id else uuid.uuid4()
    issue.title = "Test Issue"
    issue.description = "Test description"
    issue.category = category
    issue.severity = severity
    issue.status = status
    issue.created_at = datetime.now(tz=timezone.utc)
    issue.updated_at = datetime.now(tz=timezone.utc)
    issue.resolved_at = None
    issue.context_json = "{}"
    issue.entity_id = None
    return issue


class TestCreateIssue:
    @pytest.mark.asyncio
    async def test_create_issue_adds_to_db(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()

        issue = await create_issue(
            db,
            title="LCR Breach",
            description="LCR fell below 100%",
            category="liquidity",
            severity="critical",
        )

        db.add.assert_called_once()
        db.flush.assert_called_once()
        assert issue.title == "LCR Breach"
        assert issue.status == "open"

    @pytest.mark.asyncio
    async def test_create_issue_default_category(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()

        issue = await create_issue(db, title="Test", description="Desc")
        assert issue.category == "regulatory"

    @pytest.mark.asyncio
    async def test_create_issue_with_entity_id(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()

        eid = str(uuid.uuid4())
        issue = await create_issue(db, title="T", description="D", entity_id=eid)
        assert issue.entity_id is not None


class TestUpdateIssueStatus:
    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        db = AsyncMock()
        db.get = AsyncMock(return_value=None)

        result = await update_issue_status(db, issue_id=str(uuid.uuid4()), status="resolved")
        assert result is None

    @pytest.mark.asyncio
    async def test_updates_status_to_resolved(self):
        db = AsyncMock()
        mock_issue = _make_mock_issue()
        db.get = AsyncMock(return_value=mock_issue)
        db.flush = AsyncMock()

        result = await update_issue_status(db, issue_id=str(mock_issue.id), status="resolved")
        assert mock_issue.status == "resolved"
        assert mock_issue.resolved_at is not None

    @pytest.mark.asyncio
    async def test_updates_status_to_monitoring(self):
        db = AsyncMock()
        mock_issue = _make_mock_issue()
        db.get = AsyncMock(return_value=mock_issue)
        db.flush = AsyncMock()

        result = await update_issue_status(db, issue_id=str(mock_issue.id), status="monitoring")
        assert mock_issue.status == "monitoring"

    @pytest.mark.asyncio
    async def test_invalid_status_raises_value_error(self):
        db = AsyncMock()
        mock_issue = _make_mock_issue()
        db.get = AsyncMock(return_value=mock_issue)

        with pytest.raises(ValueError, match="Invalid status"):
            await update_issue_status(db, issue_id=str(mock_issue.id), status="invalid_status")


class TestListIssues:
    @pytest.mark.asyncio
    async def test_returns_list(self):
        db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        db.execute = AsyncMock(return_value=mock_result)

        result = await list_issues(db)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_returns_issues(self):
        db = AsyncMock()
        issues = [_make_mock_issue(), _make_mock_issue(status="monitoring")]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = issues
        db.execute = AsyncMock(return_value=mock_result)

        result = await list_issues(db)
        assert len(result) == 2
