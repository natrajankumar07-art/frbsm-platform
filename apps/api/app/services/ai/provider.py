"""
AI provider abstraction layer.

Designed for extensibility: Anthropic is the initial provider.
OpenAI, Gemini, Azure OpenAI, and local models can be added by
implementing the AIProvider ABC without touching frontend or orchestration code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class StreamToken:
    content: str
    is_final: bool = False
    tokens_in: int = 0
    tokens_out: int = 0
    model: str = ""


class ProviderError(Exception):
    """Raised when an AI provider returns an error."""


class AIProvider(ABC):
    """Abstract base for all AI providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @abstractmethod
    def stream_chat(
        self,
        messages: list[ChatMessage],
        system: str,
        max_tokens: int = 2048,
    ) -> AsyncIterator[StreamToken]: ...


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider using the official async SDK."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6") -> None:
        self._api_key = api_key
        self._model = model
        # Lazy import: only require anthropic if this provider is instantiated
        import anthropic  # noqa: PLC0415

        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def model_name(self) -> str:
        return self._model

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        system: str,
        max_tokens: int = 2048,
    ) -> AsyncIterator[StreamToken]:
        import anthropic  # noqa: PLC0415

        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role in ("user", "assistant")
        ]

        try:
            async with self._client.messages.stream(
                model=self._model,
                system=system,
                messages=anthropic_messages,
                max_tokens=max_tokens,
            ) as stream:
                async for text in stream.text_stream:
                    yield StreamToken(content=text)

                final = await stream.get_final_message()
                usage = final.usage
                yield StreamToken(
                    content="",
                    is_final=True,
                    tokens_in=usage.input_tokens,
                    tokens_out=usage.output_tokens,
                    model=self._model,
                )
        except anthropic.APIError as exc:
            raise ProviderError(str(exc)) from exc


# ---------------------------------------------------------------------------
# Future providers (stubs — implement when needed)
# ---------------------------------------------------------------------------

# class OpenAIProvider(AIProvider):
#     """OpenAI / Azure OpenAI provider."""
#     ...

# class GeminiProvider(AIProvider):
#     """Google Gemini provider."""
#     ...

# class LocalModelProvider(AIProvider):
#     """Ollama / llama.cpp local model provider."""
#     ...
