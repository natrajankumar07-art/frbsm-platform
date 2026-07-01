"""
Conversation memory for the FRBSM AI Copilot (Epic 4C).

Persists session state (active entity, snapshot, recent refs, report history)
in the copilot_sessions.session_context JSON column. Works alongside the
existing copilot_messages history from Epic 4A — this is purely additive.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models.copilot import CopilotSessionModel

_MAX_RECENT = 5  # Max items in recent_* lists
_MAX_TOOL_CALLS = 10


@dataclass
class SessionMemory:
    """In-session conversation context, persisted between turns."""

    active_entity_id: str | None = None
    active_snapshot_id: str | None = None
    active_entity_name: str | None = None
    active_snapshot_date: str | None = None
    recent_snapshot_ids: list[str] = field(default_factory=list)
    recent_entity_ids: list[str] = field(default_factory=list)
    report_history: list[dict] = field(default_factory=list)
    last_tool_calls: list[dict] = field(default_factory=list)

    def set_active_entity(self, entity_id: str, entity_name: str) -> None:
        self.active_entity_id = entity_id
        self.active_entity_name = entity_name
        if entity_id not in self.recent_entity_ids:
            self.recent_entity_ids.insert(0, entity_id)
            self.recent_entity_ids = self.recent_entity_ids[:_MAX_RECENT]

    def set_active_snapshot(self, snapshot_id: str, snapshot_date: str) -> None:
        self.active_snapshot_id = snapshot_id
        self.active_snapshot_date = snapshot_date
        if snapshot_id not in self.recent_snapshot_ids:
            self.recent_snapshot_ids.insert(0, snapshot_id)
            self.recent_snapshot_ids = self.recent_snapshot_ids[:_MAX_RECENT]

    def record_tool_call(self, tool_name: str, summary: str) -> None:
        entry = {
            "tool": tool_name,
            "summary": summary[:200],
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
        self.last_tool_calls.insert(0, entry)
        self.last_tool_calls = self.last_tool_calls[:_MAX_TOOL_CALLS]

    def record_report(self, report_type: str) -> None:
        entry = {
            "report_type": report_type,
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        self.report_history.insert(0, entry)
        self.report_history = self.report_history[:_MAX_RECENT]

    def build_context_preamble(self) -> str:
        """Return a short context string for injection into system prompt."""
        parts: list[str] = []
        if self.active_entity_name and self.active_snapshot_date:
            parts.append(
                f"Active context: {self.active_entity_name} | "
                f"Snapshot: {self.active_snapshot_date}"
            )
        if self.last_tool_calls:
            last = self.last_tool_calls[0]
            parts.append(f"Last tool: {last['tool']} — {last['summary']}")
        if self.report_history:
            last_rpt = self.report_history[0]
            parts.append(f"Last report: {last_rpt['report_type']} ({last_rpt['generated_at'][:10]})")
        return " | ".join(parts) if parts else ""

    def resolve_reference(self, reference: str | None) -> dict:
        """
        Resolve a conversational reference from session memory.

        Returns a dict with resolved keys relevant to the reference type.
        Used by the SAM Planner (Epic 4D) to resolve phrases like
        "same entity", "last month", "generate another report".
        """
        if not reference:
            return {}

        if reference == "active_entity":
            return {
                "entity_id": self.active_entity_id,
                "entity_name": self.active_entity_name,
            }

        if reference == "active_snapshot":
            return {
                "snapshot_id": self.active_snapshot_id,
                "snapshot_date": self.active_snapshot_date,
            }

        if reference in ("previous_month", "previous_quarter", "previous_year", "previous_day", "previous_period"):
            # Return the second most-recent snapshot if available
            if len(self.recent_snapshot_ids) >= 2:
                return {"snapshot_id": self.recent_snapshot_ids[1]}
            return {"snapshot_id": self.active_snapshot_id}

        if reference == "repeat_analysis":
            # Return last tool call info so planner can replicate it
            if self.last_tool_calls:
                last = self.last_tool_calls[0]
                return {"repeat_tool": last.get("tool"), "repeat_summary": last.get("summary")}
            return {}

        if reference == "repeat_report":
            # Return last report type for re-generation
            if self.report_history:
                last_rpt = self.report_history[0]
                return {"report_type": last_rpt.get("report_type")}
            return {}

        return {}

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SessionMemory":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


async def get_session_memory(
    db: AsyncSession, session_id: uuid.UUID
) -> SessionMemory:
    """Load session memory from DB; return empty SessionMemory if not found."""
    session = await db.scalar(
        select(CopilotSessionModel).where(CopilotSessionModel.id == session_id)
    )
    if not session or not session.session_context:
        return SessionMemory()

    try:
        data = json.loads(session.session_context)
        return SessionMemory.from_dict(data)
    except (json.JSONDecodeError, TypeError):
        return SessionMemory()


async def update_session_memory(
    db: AsyncSession, session_id: uuid.UUID, memory: SessionMemory
) -> None:
    """Persist session memory to DB."""
    await db.execute(
        update(CopilotSessionModel)
        .where(CopilotSessionModel.id == session_id)
        .values(session_context=json.dumps(memory.to_dict()))
    )
    await db.flush()
