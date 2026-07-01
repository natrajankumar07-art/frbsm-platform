"""Base types for the Banking Intelligence reasoning layer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ReasoningContext:
    """Carries all engine data needed by one or more reasoning modules."""

    user_message: str
    entity_name: str = ""
    snapshot_date: str = ""
    lcr: dict | None = None
    nsfr: dict | None = None
    capital: dict | None = None
    balance_sheet: dict | None = None
    # Populated by reasoning_engine.classify_intent; used for module routing
    detected_domains: list[str] = field(default_factory=list)


class ReasoningModule(ABC):
    """Abstract base for all seven Banking Intelligence reasoning modules."""

    @property
    @abstractmethod
    def domain(self) -> str:
        """Short machine-readable domain key (e.g. 'liquidity', 'capital')."""

    @abstractmethod
    def is_relevant(self, ctx: ReasoningContext) -> bool:
        """Return True when this module should contribute to the response."""

    @abstractmethod
    def build_prompt_extension(self, ctx: ReasoningContext) -> str:
        """Return a prompt extension string to append to the system prompt."""
