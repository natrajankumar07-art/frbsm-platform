"""
Epic 4C — AI Workflow and Report Automation endpoints.

  POST /v1/copilot/workflow/chat       — agentic tool-calling chat (SSE)
  POST /v1/copilot/tools/execute       — direct tool execution (JSON)
  GET  /v1/copilot/tools               — list all 15 tools with schemas
  POST /v1/copilot/reports/generate    — generate a Markdown report
  GET  /v1/copilot/reports/types       — list all 10 report types
  GET  /v1/copilot/sessions/{id}/memory — get session memory state

These endpoints are additive; they do not modify Epic 4A or 4B infrastructure.
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..config import settings
from ..dependencies import DBSession
from ..schemas.workflow import (
    ReportGenerateRequest,
    ReportResponse,
    ReportTypeInfo,
    SessionMemoryResponse,
    ToolExecuteRequest,
    ToolExecuteResponse,
    ToolInfo,
    WorkflowChatRequest,
)
from ..services.ai.memory import get_session_memory, update_session_memory
from ..services.ai.reports.base import ReportType
from ..services.ai.reports.generators import generate_report
from ..services.ai.tools import registry
from ..services.ai.workflow_executor import execute_workflow

router = APIRouter(prefix="/v1/copilot", tags=["AI Workflow"])
logger = structlog.get_logger(__name__)

_REPORT_TYPES = [
    ReportTypeInfo(id=rt.value, name=rt.display_name, description=rt.description)
    for rt in ReportType
]


# ---------------------------------------------------------------------------
# Agentic workflow chat (SSE, tool-calling)
# ---------------------------------------------------------------------------

@router.post("/workflow/chat")
async def workflow_chat(
    body: WorkflowChatRequest,
    db: DBSession,
) -> StreamingResponse:
    """
    Agentic chat with AI tool calling. Claude decides which tool to invoke;
    the server executes it and feeds results back. Up to 3 tool-call rounds.
    Returns SSE stream with tool_call, tool_result, token, and done events.
    """
    memory = await get_session_memory(db, body.session_id)

    # Build system prompt with memory context preamble
    from ..services.ai.context import build_financial_context, get_financial_data  # noqa: PLC0415
    from ..services.ai.prompts import COPILOT_SYSTEM_PROMPT  # noqa: PLC0415
    from ..services.ai.reasoning_engine import build_enriched_system_prompt, build_reasoning_context  # noqa: PLC0415

    financial_context = await build_financial_context(db, body.entity_id, body.snapshot_id)
    financial_data = await get_financial_data(db, body.entity_id, body.snapshot_id)

    if financial_data:
        reasoning_ctx = await build_reasoning_context(
            user_message=body.user_message,
            entity_name=financial_data.get("entity_name", ""),
            snapshot_date=financial_data.get("snapshot_date", ""),
            financial_data=financial_data,
        )
        base = COPILOT_SYSTEM_PROMPT
        if financial_context:
            base = f"{COPILOT_SYSTEM_PROMPT}\n\n{financial_context}"
        system_prompt = build_enriched_system_prompt(base, reasoning_ctx)
    else:
        system_prompt = COPILOT_SYSTEM_PROMPT

    # Inject memory context
    mem_preamble = memory.build_context_preamble()
    if mem_preamble:
        system_prompt = f"{system_prompt}\n\n[CONVERSATION CONTEXT]\n{mem_preamble}"

    # Inject tool usage instruction
    tool_names = ", ".join(registry.tool_names())
    system_prompt += (
        f"\n\n[WORKFLOW MODE]\nYou have access to 15 banking tools: {tool_names}. "
        "Use them to retrieve live data before answering. "
        "Always cite the tool result evidence in your response."
    )

    async def _stream():
        async for event in execute_workflow(
            db=db,
            api_key=settings.anthropic_api_key or "",
            model=settings.anthropic_model,
            session_id=body.session_id,
            user_message=body.user_message,
            entity_id=body.entity_id,
            snapshot_id=body.snapshot_id,
            registry=registry,
            memory=memory,
            system_prompt=system_prompt,
        ):
            yield event

    return StreamingResponse(_stream(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Direct tool execution
# ---------------------------------------------------------------------------

@router.post("/tools/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    body: ToolExecuteRequest,
    db: DBSession,
) -> ToolExecuteResponse:
    """Execute a specific tool by name with the provided parameters."""
    tool = registry.get(body.tool_name)
    if not tool:
        return ToolExecuteResponse(
            success=False,
            tool_name=body.tool_name,
            data={},
            evidence={},
            markdown="",
            error=f"Tool '{body.tool_name}' not found. Use GET /v1/copilot/tools to list available tools.",
        )

    # Inject entity/snapshot into params if provided and not already present
    params = dict(body.params)
    if body.entity_id and "entity_id" not in params:
        params["entity_id"] = str(body.entity_id)
    if body.snapshot_id and "snapshot_id" not in params:
        params["snapshot_id"] = str(body.snapshot_id)

    result = await tool.execute(params, db)
    logger.info("tool_executed", tool=body.tool_name, success=result.success)

    return ToolExecuteResponse(
        success=result.success,
        tool_name=result.tool_name,
        data=result.data,
        evidence=result.evidence.to_dict(),
        markdown=result.markdown,
        error=result.error,
    )


# ---------------------------------------------------------------------------
# Tool discovery
# ---------------------------------------------------------------------------

@router.get("/tools", response_model=list[ToolInfo])
async def list_tools() -> list[ToolInfo]:
    """List all 15 AI workflow tools with their input schemas."""
    return [
        ToolInfo(
            name=t.name,
            description=t.description,
            input_schema=t.input_schema,
        )
        for t in registry.all_tools()
    ]


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

@router.post("/reports/generate", response_model=ReportResponse)
async def generate_report_endpoint(
    body: ReportGenerateRequest,
    db: DBSession,
) -> ReportResponse:
    """Generate a Markdown report of the specified type from stored engine data."""
    try:
        report_type = ReportType(body.report_type)
    except ValueError:
        valid = ", ".join(rt.value for rt in ReportType)
        return ReportResponse(
            report_type=body.report_type,
            title="Invalid Report Type",
            entity="",
            snapshot_date="",
            generated_at="",
            content_markdown=f"Invalid report type. Valid types: {valid}",
            evidence={},
            export_hints={},
        )

    report = await generate_report(
        db=db,
        report_type=report_type,
        entity_id=body.entity_id,
        snapshot_id=body.snapshot_id,
    )
    logger.info("report_generated", report_type=report_type.value, entity=report.entity)

    return ReportResponse(**report.to_dict())


@router.get("/reports/types", response_model=list[ReportTypeInfo])
async def list_report_types() -> list[ReportTypeInfo]:
    """List all 10 available report types."""
    return _REPORT_TYPES


# ---------------------------------------------------------------------------
# Conversation memory
# ---------------------------------------------------------------------------

@router.get("/sessions/{session_id}/memory", response_model=SessionMemoryResponse)
async def get_memory(
    session_id: uuid.UUID,
    db: DBSession,
) -> SessionMemoryResponse:
    """Retrieve the conversation memory state for a session."""
    memory = await get_session_memory(db, session_id)
    return SessionMemoryResponse(
        session_id=session_id,
        active_entity_id=memory.active_entity_id,
        active_entity_name=memory.active_entity_name,
        active_snapshot_id=memory.active_snapshot_id,
        active_snapshot_date=memory.active_snapshot_date,
        recent_entity_ids=memory.recent_entity_ids,
        recent_snapshot_ids=memory.recent_snapshot_ids,
        report_history=memory.report_history,
        last_tool_calls=memory.last_tool_calls,
    )
