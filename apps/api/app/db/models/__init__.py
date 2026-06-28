"""ORM model registry — import all models here so Alembic autogenerate sees them."""

from .audit_log import AuditLogEntry
from .balance_sheet import BalanceSheetLineItemModel, BalanceSheetSummaryModel
from .capital import CapitalResultModel
from .cashflow import CashflowModel, CashflowProjectionModel
from .compute_run import ComputeRunModel
from .counterparty import CounterpartyModel
from .lcr import (
    LCRHQLAComponentModel,
    LCRInflowComponentModel,
    LCROutflowComponentModel,
    LCRResultModel,
)
from .legal_entity import EntityCapitalRequirementModel, LegalEntityModel
from .nsfr import NSFRASFComponentModel, NSFRResultModel, NSFRRSFComponentModel
from .position import CollateralModel, PositionModel
from .product_catalog import (
    ProductBehavioralAssumptionModel,
    ProductGroupModel,
    ProductModel,
)
from .reasoning_run import ReasoningRunModel
from .reference_data import (
    CreditConversionFactorModel,
    HQLAHaircutModel,
    RiskWeightModel,
    RunOffRateModel,
    YieldCurveModel,
)
from .regulatory import (
    RegulatoryFilingLineageModel,
    RegulatoryFilingModel,
    RegulatoryParameterHistoryModel,
)
from .scenario import ScenarioModel, ScenarioParameterSetModel
from .snapshot import SnapshotModel
from .stress_test import StressPositionImpactModel, StressTestResultModel, StressTestRunModel
from .structural_liquidity import StructuralLiquidityBucketModel
from .workflow import CloseTaskModel, SignOffModel, WorkpaperModel

__all__ = [
    # Audit
    "AuditLogEntry",
    # Balance sheet
    "BalanceSheetLineItemModel",
    "BalanceSheetSummaryModel",
    # Capital
    "CapitalResultModel",
    # Cashflows
    "CashflowModel",
    "CashflowProjectionModel",
    # Compute
    "ComputeRunModel",
    # Counterparty & position
    "CounterpartyModel",
    "CollateralModel",
    "PositionModel",
    # LCR
    "LCRHQLAComponentModel",
    "LCRInflowComponentModel",
    "LCROutflowComponentModel",
    "LCRResultModel",
    # Legal entities
    "EntityCapitalRequirementModel",
    "LegalEntityModel",
    # NSFR
    "NSFRASFComponentModel",
    "NSFRResultModel",
    "NSFRRSFComponentModel",
    # Product catalog
    "ProductBehavioralAssumptionModel",
    "ProductGroupModel",
    "ProductModel",
    # Reasoning
    "ReasoningRunModel",
    # Reference data
    "CreditConversionFactorModel",
    "HQLAHaircutModel",
    "RiskWeightModel",
    "RunOffRateModel",
    "YieldCurveModel",
    # Regulatory
    "RegulatoryFilingLineageModel",
    "RegulatoryFilingModel",
    "RegulatoryParameterHistoryModel",
    # Scenarios
    "ScenarioModel",
    "ScenarioParameterSetModel",
    # Snapshot
    "SnapshotModel",
    # Stress testing
    "StressPositionImpactModel",
    "StressTestResultModel",
    "StressTestRunModel",
    # Structural liquidity (SLS)
    "StructuralLiquidityBucketModel",
    # Workflow
    "CloseTaskModel",
    "SignOffModel",
    "WorkpaperModel",
]
