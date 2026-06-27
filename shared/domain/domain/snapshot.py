"""Snapshot domain model — point-in-time frozen view of positions and reference data."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .enums import SnapshotStatus


class Snapshot(BaseModel):
    """
    An immutable, content-addressed snapshot of position and reference data at a reporting date.

    Snapshots are the contract between the data layer and the compute engines.
    Every engine receives a Snapshot (not raw mutable positions).

    Invariants:
    - Once status transitions to LOCKED, no position or reference data may change.
    - position_hash and reference_hash are SHA-256 hexdigests of the serialised
      position set and reference data set at freeze time.
    - Recomputing the hash from the snapshot's positions must always match position_hash.

    Lifecycle: DRAFT → LOCKED → FILED
    """

    model_config = {"frozen": True}

    id: UUID
    reporting_date_iso: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    frozen_at: datetime
    frozen_by: str = Field(..., min_length=1)  # user_id
    position_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")  # SHA-256 hex
    reference_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    position_count: int = Field(..., ge=0)
    status: SnapshotStatus = SnapshotStatus.DRAFT
    notes: str | None = None

    @property
    def is_immutable(self) -> bool:
        return self.status in (SnapshotStatus.LOCKED, SnapshotStatus.FILED)
