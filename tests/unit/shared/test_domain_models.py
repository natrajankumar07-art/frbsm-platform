"""Round-trip serialization and field constraint tests for domain models."""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from domain.position import Position
from domain.enums import IFRS9Stage, SnapshotStatus
from domain.snapshot import Snapshot


def _make_snapshot(**overrides: object) -> Snapshot:
    """Construct a minimal valid Snapshot, merging any field overrides."""
    defaults: dict = {
        "id": uuid.uuid4(),
        "reporting_date": date(2024, 3, 31),
        "frozen_at": datetime(2024, 3, 31, 18, 0, 0, tzinfo=timezone.utc),
        "frozen_by": "user-001",
        "position_hash": "a" * 64,
        "reference_hash": "b" * 64,
        "position_count": 0,
        "status": SnapshotStatus.DRAFT,
    }
    defaults.update(overrides)
    return Snapshot(**defaults)


class TestPositionRoundTrip:
    def test_model_dump_and_reconstruct(self, minimal_position: Position) -> None:
        data = minimal_position.model_dump()
        reconstructed = Position.model_validate(data)
        assert reconstructed == minimal_position

    def test_json_round_trip(self, minimal_position: Position) -> None:
        json_str = minimal_position.model_dump_json()
        reconstructed = Position.model_validate_json(json_str)
        assert reconstructed == minimal_position

    def test_position_is_frozen(self, minimal_position: Position) -> None:
        with pytest.raises((TypeError, ValidationError)):
            minimal_position.notional = Decimal("999")  # type: ignore[misc]

    def test_maturity_must_be_after_reporting_date(self, minimal_position: Position) -> None:
        data = minimal_position.model_dump()
        # maturity_date earlier than reporting_date should fail for active positions
        data["maturity_date"] = date(2024, 1, 1)  # before reporting_date 2024-03-31
        with pytest.raises(ValidationError):
            Position.model_validate(data)

    def test_notional_must_be_non_negative(self, minimal_position: Position) -> None:
        data = minimal_position.model_dump()
        data["notional"] = Decimal("-1.00")
        with pytest.raises(ValidationError):
            Position.model_validate(data)

    def test_days_past_due_non_negative(self, minimal_position: Position) -> None:
        data = minimal_position.model_dump()
        data["days_past_due"] = -1
        with pytest.raises(ValidationError):
            Position.model_validate(data)


class TestSnapshotStatus:
    def test_draft_is_not_immutable(self) -> None:
        snap = _make_snapshot(status=SnapshotStatus.DRAFT)
        assert not snap.is_immutable

    def test_locked_is_immutable(self) -> None:
        snap = _make_snapshot(status=SnapshotStatus.LOCKED)
        assert snap.is_immutable

    def test_filed_is_immutable(self) -> None:
        snap = _make_snapshot(status=SnapshotStatus.FILED)
        assert snap.is_immutable

    def test_snapshot_is_frozen(self) -> None:
        snap = _make_snapshot()
        with pytest.raises((TypeError, ValidationError)):
            snap.status = SnapshotStatus.FILED  # type: ignore[misc]

    def test_position_hash_must_be_64_hex_chars(self) -> None:
        with pytest.raises(ValidationError):
            _make_snapshot(position_hash="not-a-sha256")

    def test_reference_hash_must_be_64_hex_chars(self) -> None:
        with pytest.raises(ValidationError):
            _make_snapshot(reference_hash="zz" * 32)  # non-hex chars

    def test_json_round_trip(self) -> None:
        snap = _make_snapshot()
        reconstructed = Snapshot.model_validate_json(snap.model_dump_json())
        assert reconstructed == snap
