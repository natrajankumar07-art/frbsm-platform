"""Round-trip serialization and field constraint tests for domain models."""
from __future__ import annotations

import json
from decimal import Decimal
from datetime import date

import pytest
from pydantic import ValidationError

from domain.position import Position
from domain.enums import IFRS9Stage, SnapshotStatus
from domain.snapshot import Snapshot


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
        # maturity_date earlier than reporting_date should fail
        data["maturity_date"] = date(2024, 1, 1)  # before reporting_date 2024-03-31
        with pytest.raises(ValidationError):
            Position.model_validate(data)

    def test_notional_must_be_positive(self, minimal_position: Position) -> None:
        data = minimal_position.model_dump()
        data["notional"] = Decimal("-1.00")
        with pytest.raises(ValidationError):
            Position.model_validate(data)

    def test_pd_must_be_between_zero_and_one(self, minimal_position: Position) -> None:
        data = minimal_position.model_dump()
        data["pd_one_year"] = Decimal("1.5")
        with pytest.raises(ValidationError):
            Position.model_validate(data)

    def test_lgd_must_be_between_zero_and_one(self, minimal_position: Position) -> None:
        data = minimal_position.model_dump()
        data["lgd"] = Decimal("-0.01")
        with pytest.raises(ValidationError):
            Position.model_validate(data)


class TestSnapshotStatus:
    def test_draft_is_not_immutable(self) -> None:
        snap = Snapshot(
            snapshot_id="SNAP-001",
            tenant_id="TENANT-001",
            reporting_date=date(2024, 3, 31),
            status=SnapshotStatus.DRAFT,
            position_count=0,
            position_hash="a" * 64,
            reference_hash="b" * 64,
        )
        assert not snap.is_immutable

    def test_locked_is_immutable(self) -> None:
        snap = Snapshot(
            snapshot_id="SNAP-001",
            tenant_id="TENANT-001",
            reporting_date=date(2024, 3, 31),
            status=SnapshotStatus.LOCKED,
            position_count=0,
            position_hash="a" * 64,
            reference_hash="b" * 64,
        )
        assert snap.is_immutable

    def test_position_hash_must_be_64_hex_chars(self) -> None:
        with pytest.raises(ValidationError):
            Snapshot(
                snapshot_id="SNAP-001",
                tenant_id="TENANT-001",
                reporting_date=date(2024, 3, 31),
                status=SnapshotStatus.DRAFT,
                position_count=0,
                position_hash="not-a-sha256",
                reference_hash="b" * 64,
            )
