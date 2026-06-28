"""Engine audit trail — EngineTrace and EngineResult wrappers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class EngineTrace(BaseModel):
    """Audit metadata attached to every engine output."""

    model_config = {"frozen": True}

    engine: str
    version: str
    function: str
    inputs_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    outputs_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    computed_at: datetime
    formula_refs: list[str]


class EngineResult(BaseModel, Generic[T]):
    """
    Container pairing a typed engine result with its audit trace.

    Usage::

        result: EngineResult[LCRResult] = compute_lcr(inputs)
        ratio = result.result.lcr_ratio      # business value
        hash_ = result.trace.inputs_hash     # audit value
    """

    result: T
    trace: EngineTrace


def build_trace(
    *,
    engine: str,
    version: str,
    function: str,
    inputs_hash: str,
    outputs_hash: str,
    formula_refs: list[str],
) -> EngineTrace:
    return EngineTrace(
        engine=engine,
        version=version,
        function=function,
        inputs_hash=inputs_hash,
        outputs_hash=outputs_hash,
        computed_at=datetime.now(tz=timezone.utc),
        formula_refs=formula_refs,
    )
