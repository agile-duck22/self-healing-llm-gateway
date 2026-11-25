"""FastAPI entry point for the gateway."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, status

from backend.app.config import GatewaySettings
from backend.app.gateway import (
    Gateway,
    GatewayTimeoutError,
    NoEligibleProviderError,
)
from backend.app.models import ChatRequest, ChatResponse, HealthResponse
from backend.app.providers import ProviderUnavailableError, SimulatedProvider


def create_app(
    *,
    settings: GatewaySettings | None = None,
    simulated_provider: SimulatedProvider | None = None,
) -> FastAPI:
    resolved_settings = settings or GatewaySettings.from_environment()
    provider = simulated_provider or SimulatedProvider()
    gateway = Gateway(resolved_settings, {provider.name: provider})

    application = FastAPI(title="Self-Healing LLM Gateway", version="0.1.0")
    application.state.gateway = gateway
    application.state.simulated_provider = provider

    @application.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        provider_status = "healthy" if provider.healthy else "unhealthy"
        return HealthResponse(providers={provider.name: provider_status})

    @application.post("/v1/chat/completions", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        try:
            return await gateway.complete(request)
        except GatewayTimeoutError as error:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=str(error),
            ) from error
        except (NoEligibleProviderError, ProviderUnavailableError) as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(error),
            ) from error

    return application


app = create_app()
