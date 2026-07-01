"""Pydantic schemas for the AI Copilot API."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    session_id: uuid.UUID | None = None
    entity_id: uuid.UUID | None = None
    snapshot_id: uuid.UUID | None = None


class SessionResponse(BaseModel):
    id: uuid.UUID
    title: str
    entity_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    model_version: str | None
    tokens_in: int | None
    tokens_out: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CopilotStatus(BaseModel):
    provider: str
    model: str
    ready: bool


class SuggestedPrompt(BaseModel):
    category: str
    text: str
