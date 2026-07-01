"""
Unit tests for the Epic 4C tool registry and tool infrastructure.
"""

import pytest

from app.services.ai.tools import registry
from app.services.ai.tools.base import BaseTool, ToolEvidence, ToolRegistry, ToolResult
from app.services.ai.tools.entity_tools import CompareEntitiesTool, ListEntitiesTool
from app.services.ai.tools.snapshot_tools import (
    CompareSnapshotsTool,
    ExplainChangesTool,
    GetSnapshotsTool,
)
from app.services.ai.tools.stress_tools import (
    CompareStressScenariosTool,
    RunStressScenarioTool,
)
from app.services.ai.tools.analysis_tools import (
    GenerateBasel3ComplianceTool,
    GenerateBoardCommentaryTool,
    GenerateCEOCommentaryTool,
    GenerateCROCommentaryTool,
    GenerateExecutiveSummaryTool,
    GenerateICAAPSummaryTool,
    GenerateILAAPSummaryTool,
    SummarizeRegulatoryResultsTool,
)


# ── ToolEvidence ───────────────────────────────────────────────────────────

class TestToolEvidence:
    def test_default_confidence_is_high(self):
        e = ToolEvidence()
        assert e.confidence == "HIGH"

    def test_to_dict_has_required_keys(self):
        e = ToolEvidence(entity="Test Bank", snapshot_date="2026-03-31")
        d = e.to_dict()
        assert "entity" in d
        assert "snapshot_date" in d
        assert "engines_used" in d
        assert "regulatory_refs" in d
        assert "source_tables" in d
        assert "confidence" in d

    def test_to_markdown_includes_entity(self):
        e = ToolEvidence(entity="BSM Demo Bank", confidence="HIGH")
        md = e.to_markdown()
        assert "BSM Demo Bank" in md

    def test_to_markdown_includes_confidence(self):
        e = ToolEvidence(confidence="MEDIUM")
        md = e.to_markdown()
        assert "MEDIUM" in md

    def test_empty_evidence_is_valid(self):
        e = ToolEvidence()
        d = e.to_dict()
        assert d["entity"] == ""
        assert d["confidence"] == "HIGH"


# ── ToolResult ─────────────────────────────────────────────────────────────

class TestToolResult:
    def test_to_dict_has_required_keys(self):
        r = ToolResult(
            success=True,
            tool_name="test_tool",
            data={"key": "value"},
            evidence=ToolEvidence(),
            markdown="# Result",
        )
        d = r.to_dict()
        assert "success" in d
        assert "tool_name" in d
        assert "data" in d
        assert "evidence" in d
        assert "markdown" in d
        assert "error" in d

    def test_error_result_is_unsuccessful(self):
        r = ToolResult(
            success=False,
            tool_name="failing_tool",
            data={},
            evidence=ToolEvidence(),
            markdown="Error",
            error="Something went wrong",
        )
        assert not r.success
        assert r.error == "Something went wrong"


# ── ToolRegistry ───────────────────────────────────────────────────────────

class TestToolRegistry:
    def test_registry_has_15_tools(self):
        assert len(registry) == 15

    def test_registry_contains_all_required_tools(self):
        required = [
            "list_entities",
            "get_snapshots",
            "compare_snapshots",
            "compare_entities",
            "explain_changes",
            "run_stress_scenario",
            "compare_stress_scenarios",
            "summarize_regulatory_results",
            "generate_executive_summary",
            "generate_board_commentary",
            "generate_cro_commentary",
            "generate_ceo_commentary",
            "generate_icaap_summary",
            "generate_ilaap_summary",
            "generate_basel3_compliance",
        ]
        for name in required:
            assert registry.get(name) is not None, f"Missing tool: {name}"

    def test_get_unknown_tool_returns_none(self):
        assert registry.get("nonexistent_tool") is None

    def test_all_tools_returns_list(self):
        tools = registry.all_tools()
        assert isinstance(tools, list)
        assert len(tools) == 15

    def test_anthropic_schemas_returns_correct_format(self):
        schemas = registry.anthropic_schemas()
        assert len(schemas) == 15
        for schema in schemas:
            assert "name" in schema
            assert "description" in schema
            assert "input_schema" in schema

    def test_tool_names_returns_all_names(self):
        names = registry.tool_names()
        assert len(names) == 15
        assert "list_entities" in names

    def test_register_custom_tool(self):
        reg = ToolRegistry()

        class DummyTool(BaseTool):
            name = "dummy"
            description = "A dummy test tool"
            input_schema = {"type": "object", "properties": {}, "required": []}
            async def execute(self, params, db):
                return self._error_result("not implemented")

        reg.register(DummyTool())
        assert len(reg) == 1
        assert reg.get("dummy") is not None


# ── Individual tool schemas ────────────────────────────────────────────────

class TestEntityTools:
    def test_list_entities_name(self):
        assert ListEntitiesTool.name == "list_entities"

    def test_list_entities_has_description(self):
        t = ListEntitiesTool()
        assert len(t.description) > 20

    def test_list_entities_input_schema_is_dict(self):
        t = ListEntitiesTool()
        assert isinstance(t.input_schema, dict)
        assert t.input_schema.get("type") == "object"

    def test_compare_entities_requires_two_ids(self):
        t = CompareEntitiesTool()
        required = t.input_schema.get("required", [])
        assert "entity_id_a" in required
        assert "entity_id_b" in required

    def test_to_anthropic_schema_format(self):
        t = ListEntitiesTool()
        schema = t.to_anthropic_schema()
        assert schema["name"] == "list_entities"
        assert "description" in schema
        assert "input_schema" in schema

    def test_error_result_helper(self):
        t = ListEntitiesTool()
        r = t._error_result("test error")
        assert not r.success
        assert r.error == "test error"
        assert r.tool_name == "list_entities"


class TestSnapshotTools:
    def test_get_snapshots_name(self):
        assert GetSnapshotsTool.name == "get_snapshots"

    def test_compare_snapshots_requires_entity_and_both_snapshots(self):
        t = CompareSnapshotsTool()
        required = t.input_schema.get("required", [])
        assert "entity_id" in required
        assert "snapshot_id_a" in required
        assert "snapshot_id_b" in required

    def test_explain_changes_same_required_params(self):
        t = ExplainChangesTool()
        required = t.input_schema.get("required", [])
        assert "entity_id" in required


class TestStressTools:
    def test_run_stress_scenario_name(self):
        assert RunStressScenarioTool.name == "run_stress_scenario"

    def test_run_stress_requires_scenario_id(self):
        t = RunStressScenarioTool()
        required = t.input_schema.get("required", [])
        assert "scenario_id" in required

    def test_compare_stress_requires_two_scenario_ids(self):
        t = CompareStressScenariosTool()
        required = t.input_schema.get("required", [])
        assert "scenario_id_a" in required
        assert "scenario_id_b" in required


class TestAnalysisTools:
    def test_summarize_regulatory_name(self):
        assert SummarizeRegulatoryResultsTool.name == "summarize_regulatory_results"

    def test_executive_summary_name(self):
        assert GenerateExecutiveSummaryTool.name == "generate_executive_summary"

    def test_board_commentary_name(self):
        assert GenerateBoardCommentaryTool.name == "generate_board_commentary"

    def test_cro_commentary_name(self):
        assert GenerateCROCommentaryTool.name == "generate_cro_commentary"

    def test_ceo_commentary_name(self):
        assert GenerateCEOCommentaryTool.name == "generate_ceo_commentary"

    def test_icaap_summary_name(self):
        assert GenerateICAAPSummaryTool.name == "generate_icaap_summary"

    def test_ilaap_summary_name(self):
        assert GenerateILAAPSummaryTool.name == "generate_ilaap_summary"

    def test_basel3_compliance_name(self):
        assert GenerateBasel3ComplianceTool.name == "generate_basel3_compliance"

    def test_all_analysis_tools_require_entity_id(self):
        tools = [
            SummarizeRegulatoryResultsTool(),
            GenerateExecutiveSummaryTool(),
            GenerateBoardCommentaryTool(),
            GenerateCROCommentaryTool(),
            GenerateCEOCommentaryTool(),
            GenerateICAAPSummaryTool(),
            GenerateILAAPSummaryTool(),
            GenerateBasel3ComplianceTool(),
        ]
        for t in tools:
            required = t.input_schema.get("required", [])
            assert "entity_id" in required, f"{t.name} missing entity_id in required"

    def test_all_analysis_tools_snapshot_id_is_optional(self):
        t = GenerateExecutiveSummaryTool()
        required = t.input_schema.get("required", [])
        assert "snapshot_id" not in required
