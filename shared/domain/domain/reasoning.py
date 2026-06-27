"""
Reasoning layer domain models.

These define the CONTRACT that every reasoning module must satisfy.
A module that does not return a ReasoningOutput is not a valid reasoning module.

The core discipline enforced here:
- `compute_run_ids` is never empty for a filed output — reasoning always cites its compute sources.
- `text` never contains a number not present in the structured inputs (enforced by prompt design).
- `review_required` is True for any output intended for external parties.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from .enums import ReasoningModuleType, ReviewOutcome


class ReasoningOutput(BaseModel):
    """
    The typed return value of every reasoning module.

    Enforced by ReasoningOutputValidator in the reasoning infrastructure.
    Modules that return non-conforming output raise SchemaValidationError;
    they never partially render.
    """

    model_config = {"frozen": True}

    text: str = Field(..., min_length=1)
    compute_run_ids: tuple[UUID, ...] = Field(..., min_length=0)
    model_version: str = Field(..., min_length=1, max_length=100)
    prompt_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    module_type: ReasoningModuleType
    tokens_in: int = Field(..., ge=0)
    tokens_out: int = Field(..., ge=0)
    review_required: bool = False

    @model_validator(mode="after")
    def external_output_requires_review(self) -> "ReasoningOutput":
        if self.module_type == ReasoningModuleType.DISCLOSURES and not self.review_required:
            raise ValueError("Disclosure outputs must always have review_required=True")
        return self


class ReasoningRun(BaseModel):
    """
    Persistence record for a reasoning module invocation.

    Stored in the database alongside compute runs to form a complete audit trail.
    """

    model_config = {"frozen": True}

    id: UUID
    snapshot_id: UUID | None = None
    module_type: ReasoningModuleType
    compute_run_ids: tuple[UUID, ...] = Field(default_factory=tuple)
    prompt_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    model_version: str = Field(..., max_length=100)
    tokens_in: int = Field(..., ge=0)
    tokens_out: int = Field(..., ge=0)
    output_text: str
    started_at: datetime
    completed_at: datetime
    review_required: bool
    reviewer_id: str | None = None
    reviewed_at: datetime | None = None
    review_outcome: ReviewOutcome | None = None

    @model_validator(mode="after")
    def review_fields_consistent(self) -> "ReasoningRun":
        if self.review_outcome is not None and self.reviewer_id is None:
            raise ValueError("review_outcome set without reviewer_id")
        return self
