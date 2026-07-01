"""
Streaming chat orchestrator for the AI Copilot.

Coordinates: context building → provider streaming → message persistence → audit logging.
Never computes financial numbers; only reads stored engine results via context.py.
"""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.copilot import CopilotMessageModel
from ...db.models.reasoning_run import ReasoningRunModel
from .context import build_financial_context, get_financial_data
from .prompts import COPILOT_SYSTEM_PROMPT
from .provider import AIProvider, ChatMessage, ProviderError
from .reasoning_engine import build_enriched_system_prompt, build_reasoning_context

_HISTORY_LIMIT = 10


async def stream_copilot_response(
    db: AsyncSession,
    provider: AIProvider,
    session_id: uuid.UUID,
    user_message: str,
    entity_id: uuid.UUID | None,
    snapshot_id: uuid.UUID | None,
) -> AsyncIterator[str]:
    """
    Orchestrate a streaming copilot response and yield SSE-formatted strings.

    SSE event types:
      {"type": "token", "content": "..."}   — partial assistant text
      {"type": "done", "session_id": "...", "message_id": "..."}  — completion
      {"type": "error", "content": "..."}   — provider or orchestration error
    """
    started_at = datetime.now(tz=timezone.utc)

    # ── 1. Load conversation history ─────────────────────────────────────────
    history_rows = (
        await db.scalars(
            select(CopilotMessageModel)
            .where(CopilotMessageModel.session_id == session_id)
            .order_by(CopilotMessageModel.created_at.asc())
            .limit(_HISTORY_LIMIT)
        )
    ).all()

    history: list[ChatMessage] = [
        ChatMessage(role=row.role, content=row.content)
        for row in history_rows
        if row.role in ("user", "assistant")
    ]

    # ── 2. Build financial context + reasoning-enriched system prompt ─────────
    financial_context = await build_financial_context(db, entity_id, snapshot_id)
    financial_data = await get_financial_data(db, entity_id, snapshot_id)

    if financial_data:
        reasoning_ctx = await build_reasoning_context(
            user_message=user_message,
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
        if financial_context:
            system_prompt = f"{COPILOT_SYSTEM_PROMPT}\n\n{financial_context}"

    # ── 3. Persist user message ───────────────────────────────────────────────
    user_msg_row = CopilotMessageModel(
        session_id=session_id,
        role="user",
        content=user_message,
        entity_id=entity_id,
        snapshot_id=snapshot_id,
        context_json=financial_context if financial_context else None,
    )
    db.add(user_msg_row)
    await db.flush()  # get the generated id

    # Build message list for provider (history + new user message)
    messages = history + [ChatMessage(role="user", content=user_message)]

    # ── 4. Stream from provider ───────────────────────────────────────────────
    full_response = ""
    tokens_in = 0
    tokens_out = 0
    model_version = provider.model_name

    try:
        async for token in provider.stream_chat(
            messages=messages,
            system=system_prompt,
        ):
            if token.is_final:
                tokens_in = token.tokens_in
                tokens_out = token.tokens_out
                model_version = token.model or provider.model_name
            else:
                full_response += token.content
                yield f"data: {json.dumps({'type': 'token', 'content': token.content})}\n\n"

    except ProviderError as exc:
        yield f"data: {json.dumps({'type': 'error', 'content': str(exc)})}\n\n"
        yield "data: [DONE]\n\n"
        return

    # ── 5. Persist assistant message ──────────────────────────────────────────
    elapsed_ms = (datetime.now(tz=timezone.utc) - started_at).total_seconds() * 1000

    assistant_msg_row = CopilotMessageModel(
        session_id=session_id,
        role="assistant",
        content=full_response,
        entity_id=entity_id,
        snapshot_id=snapshot_id,
        model_version=model_version,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=elapsed_ms,
    )
    db.add(assistant_msg_row)
    await db.flush()

    # ── 6. Audit log to reasoning_runs ───────────────────────────────────────
    from engines.common.utils import canonical_hash  # noqa: PLC0415

    prompt_payload = {
        "system": system_prompt,
        "messages": [{"role": m.role, "content": m.content} for m in messages],
    }
    prompt_hash = canonical_hash(prompt_payload)

    reasoning_row = ReasoningRunModel(
        snapshot_id=snapshot_id,
        module_type="copilot_chat",
        compute_run_ids=[],
        prompt_hash=prompt_hash,
        model_version=model_version,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        output_text=full_response,
        started_at=started_at,
        completed_at=datetime.now(tz=timezone.utc),
        review_required=False,
    )
    db.add(reasoning_row)
    await db.flush()

    # ── 7. Done event ─────────────────────────────────────────────────────────
    yield f"data: {json.dumps({'type': 'done', 'session_id': str(session_id), 'message_id': str(assistant_msg_row.id)})}\n\n"
    yield "data: [DONE]\n\n"
