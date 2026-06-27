"""Compute run domain models — audit trail for every engine invocation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EngineVersion(BaseModel):
    """Version metadata pinned to a compute run for reproducibility."""

    model_config = {"frozen": True}

    engine_name: str = Field(..., min_length=1, max_length=50)
    function_name: str = Field(..., min_length=1, max_length=100)
    semantic_version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    git_sha: str = Field(..., pattern=r"^[a-f0-9]{40}$")


class ComputeRun(BaseModel):
    """
    Audit record for a single engine function invocation.

    Every number returned by a compute engine is associated with exactly one
    ComputeRun. Given a filed number, its ComputeRun provides:
    - The snapshot it was computed from
    - The exact function and version
    - The SHA-256 of both inputs and outputs (for bit-identical reproduction)

    This is the foundation of the platform's reproducibility guarantee.
    """

    model_config = {"frozen": True}

    id: UUID
    snapshot_id: UUID
    engine: str = Field(..., max_length=50)
    function: str = Field(..., max_length=100)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    git_sha: str = Field(..., pattern=r"^[a-f0-9]{40}$")
    inputs_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")   # SHA-256
    outputs_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")  # SHA-256
    started_at: datetime
    completed_at: datetime
    duration_ms: int = Field(..., ge=0)
    success: bool
    error_message: str | None = None

    @property
    def duration_seconds(self) -> float:
        return self.duration_ms / 1000.0
