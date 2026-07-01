"""
Base types for the AI Workflow Tool Registry (Epic 4C).

Every tool: validated input → deterministic DB read → structured output + evidence.
No tool computes financial ratios or calls financial engines directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ToolEvidence:
    """Mandatory provenance block attached to every tool result."""

    entity: str = ""
    snapshot_date: str = ""
    engines_used: list[str] = field(default_factory=list)
    regulatory_refs: list[str] = field(default_factory=list)
    source_tables: list[str] = field(default_factory=list)
    confidence: str = "HIGH"  # HIGH | MEDIUM | LOW

    def to_markdown(self) -> str:
        lines = [
            "### Evidence",
            f"- **Entity:** {self.entity or 'N/A'}",
            f"- **Snapshot Date:** {self.snapshot_date or 'N/A'}",
            f"- **Engines Used:** {', '.join(self.engines_used) if self.engines_used else 'N/A (read-only)'}",
            f"- **Regulatory References:** {'; '.join(self.regulatory_refs) if self.regulatory_refs else 'N/A'}",
            f"- **Source Tables:** {', '.join(self.source_tables) if self.source_tables else 'N/A'}",
            f"- **Confidence:** {self.confidence}",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "entity": self.entity,
            "snapshot_date": self.snapshot_date,
            "engines_used": self.engines_used,
            "regulatory_refs": self.regulatory_refs,
            "source_tables": self.source_tables,
            "confidence": self.confidence,
        }


@dataclass
class ToolResult:
    """Structured output from every tool execution."""

    success: bool
    tool_name: str
    data: dict
    evidence: ToolEvidence
    markdown: str
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "tool_name": self.tool_name,
            "data": self.data,
            "evidence": self.evidence.to_dict(),
            "markdown": self.markdown,
            "error": self.error,
        }


class BaseTool(ABC):
    """Abstract base for all 15 AI Workflow tools."""

    name: ClassVar[str]
    description: ClassVar[str]
    input_schema: ClassVar[dict]  # JSON Schema — used for Anthropic tool_use

    @abstractmethod
    async def execute(self, params: dict, db: AsyncSession) -> ToolResult:
        """Execute tool with validated params; return ToolResult."""

    def to_anthropic_schema(self) -> dict:
        """Return the Anthropic tool_use schema block for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    def _error_result(self, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.name,
            data={},
            evidence=ToolEvidence(confidence="LOW"),
            markdown=f"**Error:** {message}",
            error=message,
        )


class ToolRegistry:
    """Central registry for all AI workflow tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def all_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def anthropic_schemas(self) -> list[dict]:
        return [t.to_anthropic_schema() for t in self._tools.values()]

    def tool_names(self) -> list[str]:
        return list(self._tools.keys())

    def __len__(self) -> int:
        return len(self._tools)
