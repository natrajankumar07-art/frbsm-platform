"""
platform-domain — canonical Pydantic v2 domain models.

All platform code imports domain types from here. Never redefine these elsewhere.
"""

from .compute import ComputeRun, EngineVersion
from .counterparty import Counterparty, GroupStructure
from .enums import (
    AppMode,
    AssetClass,
    CollateralType,
    CurrencyCode,
    CustomerSegment,
    DepositType,
    HQLALevel,
    IFRS9Stage,
    IRRBBShock,
    Jurisdiction,
    PositionStatus,
    RatingGrade,
    ReasoningModuleType,
    ReviewOutcome,
    SnapshotStatus,
    UserRole,
    WorkflowTaskStatus,
)
from .position import Collateral, Position
from .reasoning import ReasoningOutput, ReasoningRun
from .reference_data import (
    CreditConversionFactor,
    HQLAHaircut,
    RiskWeight,
    RunOffRate,
    YieldCurve,
)
from .snapshot import Snapshot

__all__ = [
    # Compute
    "ComputeRun",
    "EngineVersion",
    # Counterparty
    "Counterparty",
    "GroupStructure",
    # Enums
    "AppMode",
    "AssetClass",
    "CollateralType",
    "CurrencyCode",
    "CustomerSegment",
    "DepositType",
    "HQLALevel",
    "IFRS9Stage",
    "IRRBBShock",
    "Jurisdiction",
    "PositionStatus",
    "RatingGrade",
    "ReasoningModuleType",
    "ReviewOutcome",
    "SnapshotStatus",
    "UserRole",
    "WorkflowTaskStatus",
    # Position
    "Collateral",
    "Position",
    # Reasoning
    "ReasoningOutput",
    "ReasoningRun",
    # Reference data
    "CreditConversionFactor",
    "HQLAHaircut",
    "RiskWeight",
    "RunOffRate",
    "YieldCurve",
    # Snapshot
    "Snapshot",
]
