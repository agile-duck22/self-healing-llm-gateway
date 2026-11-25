"""Deterministic local provider for development and failure tests."""

from __future__ import annotations

import asyncio

from backend.app.models import ChatMessage


class ProviderUnavailableError(RuntimeError):
    """Raised when a provider cannot currently accept a request."""


class SimulatedProvider:
    """A controllable provider that never performs a network request."""

    name = "simulated"

    def __init__(self, *, latency_seconds: float = 0.0) -> None:
        if latency_seconds < 0:
            raise ValueError("latency_seconds cannot be negative")
        self.latency_seconds = latency_seconds
        self._healthy = True

    @property
    def healthy(self) -> bool:
        return self._healthy

    def fail(self) -> None:
        self._healthy = False

    def recover(self) -> None:
        self._healthy = True

    async def complete(
        self, messages: list[ChatMessage], *, max_tokens: int
    ) -> str:
        del max_tokens
        if not self._healthy:
            raise ProviderUnavailableError("simulated provider is unavailable")
        if self.latency_seconds:
            await asyncio.sleep(self.latency_seconds)
        last_user_message = next(
            (message.content for message in reversed(messages) if message.role == "user"),
            messages[-1].content,
        )
        return f"Simulated response to: {last_user_message}"
