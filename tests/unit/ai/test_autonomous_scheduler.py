"""
Unit tests for autonomous scheduler (Epic 6).
Tests: get_scheduler_status, _should_run_morning_briefing, MONITORING_INTERVAL_SECONDS.
No DB required.
"""

from datetime import datetime, timezone

import pytest

from app.services.ai.autonomous.scheduler import (
    MONITORING_INTERVAL_SECONDS,
    _should_run_morning_briefing,
    get_scheduler_status,
)


class TestSchedulerConstants:
    def test_interval_is_900_seconds(self):
        assert MONITORING_INTERVAL_SECONDS == 900

    def test_interval_is_positive(self):
        assert MONITORING_INTERVAL_SECONDS > 0


class TestShouldRunMorningBriefing:
    def _utc(self, hour: int, minute: int) -> datetime:
        return datetime(2026, 7, 1, hour, minute, 0, tzinfo=timezone.utc)

    def test_runs_at_0600(self):
        assert _should_run_morning_briefing(self._utc(6, 0)) is True

    def test_runs_at_0610(self):
        assert _should_run_morning_briefing(self._utc(6, 10)) is True

    def test_runs_at_0614(self):
        assert _should_run_morning_briefing(self._utc(6, 14)) is True

    def test_does_not_run_at_0615(self):
        assert _should_run_morning_briefing(self._utc(6, 15)) is False

    def test_does_not_run_at_0700(self):
        assert _should_run_morning_briefing(self._utc(7, 0)) is False

    def test_does_not_run_at_midnight(self):
        assert _should_run_morning_briefing(self._utc(0, 0)) is False

    def test_does_not_run_at_1800(self):
        assert _should_run_morning_briefing(self._utc(18, 0)) is False


class TestGetSchedulerStatus:
    def test_returns_dict(self):
        status = get_scheduler_status()
        assert isinstance(status, dict)

    def test_has_running_key(self):
        status = get_scheduler_status()
        assert "running" in status
        assert isinstance(status["running"], bool)

    def test_has_interval_seconds(self):
        status = get_scheduler_status()
        assert status["interval_seconds"] == MONITORING_INTERVAL_SECONDS

    def test_has_description(self):
        status = get_scheduler_status()
        assert "description" in status
        assert isinstance(status["description"], str)
