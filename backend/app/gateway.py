"""Routing and deadline enforcement for provider calls."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping

from backend.app.config import GatewaySettings
from backend.app.models import ChatRequest, ChatResponse
from backend.app.providers import ProviderUnavailableError, SimulatedProvider


class GatewayTimeoutError(RuntimeError):
    """Raised when the request-class deadline expires."""


class NoEligibleProviderError(RuntimeError):
    """Raised when no configured provider is safe and available to use."""


class Gateway:
    def __init__(
        self,
        settings: GatewaySettings,
        providers: Mapping[str, SimulatedProvider],
    ) -> None:
        self.settings = settings
        self.providers = providers

    async def complete(self, request: ChatRequest) -> ChatResponse:
        policy = self.settings.routes[request.request_class]
        provider = next(
            (
                self.providers[name]
                for name in policy.provider_preference[: policy.attempt_budget]
                if self.settings.provider_is_eligible(name)
                and name in self.providers
            ),
            None,
        )
        if provider is None:
            raise NoEligibleProviderError("no eligible provider is configured")

        try:
            reply = await asyncio.wait_for(
                provider.complete(request.messages, max_tokens=request.max_tokens),
                timeout=policy.timeout_seconds,
            )
        except TimeoutError as error:
            raise GatewayTimeoutError(
                f"{request.request_class.value} request exceeded its deadline"
            ) from error
        except ProviderUnavailableError:
            raise

        return ChatResponse(
            provider=provider.name,
            request_class=request.request_class,
            reply=reply,
        )
