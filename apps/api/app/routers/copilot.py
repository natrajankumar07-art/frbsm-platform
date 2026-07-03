"""
AI Copilot router.

Endpoints:
  POST /v1/copilot/chat           — streaming SSE chat
  GET  /v1/copilot/sessions       — list sessions
  GET  /v1/copilot/sessions/{id}/messages — messages for a session
  DELETE /v1/copilot/sessions/{id}  — delete session + cascade
  GET  /v1/copilot/status         — provider readiness
  GET  /v1/copilot/suggested-prompts — suggested banking prompts
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, func, select

from ..config import settings
from ..db.models.copilot import CopilotMessageModel, CopilotSessionModel
from ..dependencies import AppSettings, DBSession
from ..schemas.common import PagedResponse, SortDir
from ..schemas.copilot import (
    ChatRequest,
    CopilotStatus,
    MessageResponse,
    SessionResponse,
    SuggestedPrompt,
)
from ..services.ai.orchestrator import stream_copilot_response
from ..services.ai.prompts import SUGGESTED_PROMPTS
from ..services.ai.provider import AnthropicProvider, ProviderError

router = APIRouter(prefix="/v1/copilot", tags=["Copilot"])

_MAX_TITLE_LEN = 60


def _make_title(message: str) -> str:
    if len(message) <= _MAX_TITLE_LEN:
        return message
    return message[:_MAX_TITLE_LEN] + "..."


def _get_provider(cfg: settings.__class__) -> AnthropicProvider | None:  # type: ignore[valid-type]
    if not cfg.anthropic_api_key:
        return None
    
     
    return AnthropicProvider(api_key=cfg.anthropic_api_key, model=cfg.anthropic_model)


# ---------------------------------------------------------------------------
# POST /v1/copilot/chat
# ---------------------------------------------------------------------------

@router.post("/chat")
async def chat(
    payload: ChatRequest,
    db: DBSession,
    cfg: AppSettings,
) -> StreamingResponse:
    """Stream a copilot response via Server-Sent Events."""

    async def _error_stream(msg: str) -> AsyncIterator[str]:
        import json  # noqa: PLC0415

        yield f"data: {json.dumps({'type': 'error', 'content': msg})}\n\n"
        yield "data: [DONE]\n\n"

    # Validate API key early
    provider = _get_provider(cfg)
    if provider is None:
        return StreamingResponse(
            _error_stream("ANTHROPIC_API_KEY is not configured. Set it in the .env file."),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # Resolve or create session
    session_id = payload.session_id
    if session_id is None:
        session = CopilotSessionModel(
            title=_make_title(payload.message),
            entity_id=payload.entity_id,
            user_id="demo",
        )
        db.add(session)
        await db.flush()
        session_id = session.id
    else:
        existing = await db.scalar(
            select(CopilotSessionModel).where(CopilotSessionModel.id == session_id)
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Session not found")

    async def _stream() -> AsyncIterator[str]:
        async for chunk in stream_copilot_response(
            db=db,
            provider=provider,
            session_id=session_id,  # type: ignore[arg-type]
            user_message=payload.message,
            entity_id=payload.entity_id,
            snapshot_id=payload.snapshot_id,
        ):
            yield chunk

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# GET /v1/copilot/sessions
# ---------------------------------------------------------------------------

@router.get("/sessions", response_model=PagedResponse[SessionResponse])
async def list_sessions(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> PagedResponse[SessionResponse]:
    total = (
        await db.scalar(select(func.count()).select_from(CopilotSessionModel))
    ) or 0

    rows = (
        await db.scalars(
            select(CopilotSessionModel)
            .order_by(CopilotSessionModel.updated_at.desc())
            .limit(size)
            .offset((page - 1) * size)
        )
    ).all()

    return PagedResponse.create(
        [SessionResponse.model_validate(r) for r in rows],
        total,
        page,
        size,
    )


# ---------------------------------------------------------------------------
# GET /v1/copilot/sessions/{session_id}/messages
# ---------------------------------------------------------------------------

@router.get(
    "/sessions/{session_id}/messages",
    response_model=list[MessageResponse],
)
async def get_session_messages(
    session_id: uuid.UUID,
    db: DBSession,
) -> list[MessageResponse]:
    session = await db.scalar(
        select(CopilotSessionModel).where(CopilotSessionModel.id == session_id)
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    rows = (
        await db.scalars(
            select(CopilotMessageModel)
            .where(CopilotMessageModel.session_id == session_id)
            .order_by(CopilotMessageModel.created_at.asc())
        )
    ).all()

    return [MessageResponse.model_validate(r) for r in rows]


# ---------------------------------------------------------------------------
# DELETE /v1/copilot/sessions/{session_id}
# ---------------------------------------------------------------------------

@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: uuid.UUID,
    db: DBSession,
) -> None:
    session = await db.scalar(
        select(CopilotSessionModel).where(CopilotSessionModel.id == session_id)
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.execute(
        delete(CopilotSessionModel).where(CopilotSessionModel.id == session_id)
    )


# ---------------------------------------------------------------------------
# GET /v1/copilot/status
# ---------------------------------------------------------------------------

@router.get("/status", response_model=CopilotStatus)
async def get_status(cfg: AppSettings) -> CopilotStatus:
    return CopilotStatus(
        provider="anthropic",
        model=cfg.anthropic_model,
        ready=bool(cfg.anthropic_api_key),
    )


# ---------------------------------------------------------------------------
# GET /v1/copilot/suggested-prompts
# ---------------------------------------------------------------------------

@router.get("/suggested-prompts", response_model=list[SuggestedPrompt])
async def get_suggested_prompts() -> list[SuggestedPrompt]:
    return [SuggestedPrompt(**p) for p in SUGGESTED_PROMPTS]
