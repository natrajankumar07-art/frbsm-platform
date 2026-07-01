"""
AI Workflow Executor (Epic 4C).

Orchestrates multi-turn tool-calling conversations with Claude.
The AI decides which tool to invoke; the executor runs the tool and
feeds results back. Maximum 3 tool-call rounds to prevent runaway loops.

If ANTHROPIC_API_KEY is absent, returns a graceful mock response.
Does NOT modify provider.py, orchestrator.py, or any Epic 4A/4B files.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from .memory import SessionMemory, update_session_memory
from .tools.base import ToolEvidence, ToolRegistry

_MAX_ROUNDS = 3


async def execute_workflow(
    db: AsyncSession,
    api_key: str,
    model: str,
    session_id: uuid.UUID,
    user_message: str,
    entity_id: uuid.UUID | None,
    snapshot_id: uuid.UUID | None,
    registry: ToolRegistry,
    memory: SessionMemory,
    system_prompt: str,
) -> AsyncIterator[str]:
    """
    Yield SSE-formatted events for an agentic tool-calling workflow.

    Event types:
      {"type": "tool_call",   "tool": "...", "params": {...}}
      {"type": "tool_result", "tool": "...", "success": bool, "markdown": "..."}
      {"type": "token",       "content": "..."}
      {"type": "done",        "evidence": {...}, "tool_calls_made": [...]}
      {"type": "error",       "content": "..."}
    """
    if not api_key:
        async for event in _mock_workflow(user_message, registry):
            yield event
        return

    try:
        import anthropic  # noqa: PLC0415
    except ImportError:
        yield f"data: {json.dumps({'type': 'error', 'content': 'anthropic package not installed'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    client = anthropic.AsyncAnthropic(api_key=api_key)
    tool_schemas = registry.anthropic_schemas()

    messages: list[dict] = [{"role": "user", "content": user_message}]
    tool_calls_made: list[dict] = []
    all_evidence: list[ToolEvidence] = []

    try:
        for _round in range(_MAX_ROUNDS):
            response = await client.messages.create(
                model=model,
                system=system_prompt,
                messages=messages,
                tools=tool_schemas,  # type: ignore[arg-type]
                max_tokens=4096,
            )

            # Process response content blocks
            assistant_content: list[dict] = []

            for block in response.content:
                if block.type == "text":
                    # Stream text tokens
                    text = block.text
                    # Yield in chunks to simulate streaming
                    chunk_size = 50
                    for i in range(0, len(text), chunk_size):
                        chunk = text[i : i + chunk_size]
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                    assistant_content.append({"type": "text", "text": text})

                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_params = block.input or {}
                    tool_use_id = block.id

                    yield f"data: {json.dumps({'type': 'tool_call', 'tool': tool_name, 'params': tool_params})}\n\n"

                    # Execute the tool
                    tool = registry.get(tool_name)
                    if not tool:
                        tool_result_content = {"type": "error", "content": f"Unknown tool: {tool_name}"}
                        tool_result_md = f"Tool '{tool_name}' not found in registry."
                        tool_result_is_error = True
                    else:
                        result = await tool.execute(tool_params, db)
                        tool_calls_made.append({"tool": tool_name, "success": result.success})
                        if result.evidence:
                            all_evidence.append(result.evidence)
                        tool_result_content = result.to_dict()
                        tool_result_md = result.markdown
                        tool_result_is_error = not result.success

                        # Update memory
                        memory.record_tool_call(tool_name, result.markdown[:100])
                        if result.data.get("entity"):
                            memory.active_entity_name = result.data["entity"]
                        if result.data.get("snapshot_date"):
                            memory.active_snapshot_date = result.data["snapshot_date"]

                    yield f"data: {json.dumps({'type': 'tool_result', 'tool': tool_name, 'success': not tool_result_is_error, 'markdown': tool_result_md[:500]})}\n\n"

                    assistant_content.append({
                        "type": "tool_use",
                        "id": tool_use_id,
                        "name": tool_name,
                        "input": tool_params,
                    })

                    # Add tool result to messages for next round
                    messages.append({"role": "assistant", "content": assistant_content})
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(tool_result_content)[:8000],
                        }],
                    })
                    assistant_content = []
                    break  # Start next round with updated messages

            if response.stop_reason == "end_turn":
                break

    except anthropic.APIError as exc:
        yield f"data: {json.dumps({'type': 'error', 'content': str(exc)})}\n\n"
        yield "data: [DONE]\n\n"
        return

    # Persist updated memory
    await update_session_memory(db, session_id, memory)

    # Aggregate evidence
    combined_evidence = _merge_evidence(all_evidence)

    yield f"data: {json.dumps({'type': 'done', 'evidence': combined_evidence.to_dict(), 'tool_calls_made': tool_calls_made, 'session_id': str(session_id)})}\n\n"
    yield "data: [DONE]\n\n"


def _merge_evidence(evidences: list[ToolEvidence]) -> ToolEvidence:
    if not evidences:
        return ToolEvidence()
    tables: set[str] = set()
    refs: set[str] = set()
    engines: set[str] = set()
    entities = [e.entity for e in evidences if e.entity]
    dates = [e.snapshot_date for e in evidences if e.snapshot_date]
    for e in evidences:
        tables.update(e.source_tables)
        refs.update(e.regulatory_refs)
        engines.update(e.engines_used)
    return ToolEvidence(
        entity=entities[0] if entities else "",
        snapshot_date=dates[0] if dates else "",
        engines_used=sorted(engines),
        regulatory_refs=sorted(refs),
        source_tables=sorted(tables),
        confidence="HIGH" if all(e.confidence == "HIGH" for e in evidences) else "MEDIUM",
    )


async def _mock_workflow(user_message: str, registry: ToolRegistry) -> AsyncIterator[str]:
    """Mock workflow response when ANTHROPIC_API_KEY is not configured."""
    tool_names = ", ".join(registry.tool_names()[:5]) + "..."
    response_text = (
        f"I received your message: *'{user_message}'*\n\n"
        "**AI Workflow mode** is active. I have access to 15 banking tools:\n"
        f"{tool_names}\n\n"
        "To use the live AI workflow, please configure ANTHROPIC_API_KEY in your "
        ".env file. In the meantime, you can use the Reports panel to generate "
        "formatted reports directly from engine data, or use the Chat mode for "
        "regulatory guidance."
    )

    words = response_text.split()
    for i, word in enumerate(words):
        chunk = word + (" " if i < len(words) - 1 else "")
        yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

    yield f"data: {json.dumps({'type': 'done', 'evidence': ToolEvidence(confidence='LOW').to_dict(), 'tool_calls_made': [], 'session_id': 'mock'})}\n\n"
    yield "data: [DONE]\n\n"
