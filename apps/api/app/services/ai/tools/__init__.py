"""AI Workflow tool registry — Epic 4C."""

from .analysis_tools import (
    GenerateBasel3ComplianceTool,
    GenerateBoardCommentaryTool,
    GenerateCEOCommentaryTool,
    GenerateCROCommentaryTool,
    GenerateExecutiveSummaryTool,
    GenerateICAAPSummaryTool,
    GenerateILAAPSummaryTool,
    SummarizeRegulatoryResultsTool,
)
from .base import BaseTool, ToolEvidence, ToolRegistry, ToolResult
from .entity_tools import CompareEntitiesTool, ListEntitiesTool
from .snapshot_tools import CompareSnapshotsTool, ExplainChangesTool, GetSnapshotsTool
from .stress_tools import CompareStressScenariosTool, RunStressScenarioTool

# Global registry — one instance populated at import time
registry = ToolRegistry()

for _tool in [
    ListEntitiesTool(),
    GetSnapshotsTool(),
    CompareSnapshotsTool(),
    CompareEntitiesTool(),
    ExplainChangesTool(),
    RunStressScenarioTool(),
    CompareStressScenariosTool(),
    SummarizeRegulatoryResultsTool(),
    GenerateExecutiveSummaryTool(),
    GenerateBoardCommentaryTool(),
    GenerateCROCommentaryTool(),
    GenerateCEOCommentaryTool(),
    GenerateICAAPSummaryTool(),
    GenerateILAAPSummaryTool(),
    GenerateBasel3ComplianceTool(),
]:
    registry.register(_tool)

__all__ = [
    "BaseTool",
    "ToolEvidence",
    "ToolRegistry",
    "ToolResult",
    "registry",
]
