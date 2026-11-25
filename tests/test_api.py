import asyncio
from types import MappingProxyType

import httpx
import pytest

from backend.app.config import GatewaySettings, RequestClass, RoutePolicy
from backend.app.main import create_app
from backend.app.providers import SimulatedProvider


def request(app, method: str, path: str, **kwargs) -> httpx.Response:
    async def send() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(send())


def settings(*, interactive_timeout: float = 2.0) -> GatewaySettings:
    shared = {
        "provider_preference": ("simulated",),
        "attempt_budget": 1,
        "breaker_error_threshold": 0.5,
        "latency_budget_ms": 1000,
    }
    return GatewaySettings(
        routes=MappingProxyType(
            {
                RequestClass.INTERACTIVE: RoutePolicy(
                    timeout_seconds=interactive_timeout,
                    **shared,
                ),
                RequestClass.DEFERRABLE: RoutePolicy(
                    timeout_seconds=10.0,
                    **shared,
                ),
            }
        )
    )


def valid_request(**overrides) -> dict:
    payload = {
        "messages": [{"role": "user", "content": "Hello gateway"}],
        "request_class": "interactive",
        "max_tokens": 64,
    }
    payload.update(overrides)
    return payload


def test_health_reports_simulated_provider() -> None:
    response = request(create_app(), "GET", "/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "providers": {"simulated": "healthy"},
    }


def test_valid_chat_request_returns_simulated_reply() -> None:
    response = request(
        create_app(),
        "POST",
        "/v1/chat/completions",
        json=valid_request(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider": "simulated",
        "request_class": "interactive",
        "reply": "Simulated response to: Hello gateway",
        "simulated": True,
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"messages": []},
        {"messages": [{"role": "user", "content": ""}]},
        {"messages": [{"role": "tool", "content": "unsupported"}]},
        valid_request(request_class="batch"),
        valid_request(max_tokens=0),
        valid_request(unexpected="field"),
    ],
)
def test_malformed_chat_requests_are_rejected(payload: dict) -> None:
    response = request(
        create_app(),
        "POST",
        "/v1/chat/completions",
        json=payload,
    )

    assert response.status_code == 422


def test_provider_timeout_returns_gateway_timeout() -> None:
    provider = SimulatedProvider(latency_seconds=0.05)
    app = create_app(
        settings=settings(interactive_timeout=0.001),
        simulated_provider=provider,
    )

    response = request(
        app,
        "POST",
        "/v1/chat/completions",
        json=valid_request(),
    )

    assert response.status_code == 504
    assert response.json() == {
        "detail": "interactive request exceeded its deadline"
    }


def test_provider_failure_and_recovery() -> None:
    provider = SimulatedProvider()
    app = create_app(simulated_provider=provider)
    provider.fail()

    failed_health = request(app, "GET", "/health")
    failed_chat = request(
        app,
        "POST",
        "/v1/chat/completions",
        json=valid_request(),
    )

    assert failed_health.json()["providers"] == {"simulated": "unhealthy"}
    assert failed_chat.status_code == 503
    assert failed_chat.json() == {"detail": "simulated provider is unavailable"}

    provider.recover()
    recovered_health = request(app, "GET", "/health")
    recovered_chat = request(
        app,
        "POST",
        "/v1/chat/completions",
        json=valid_request(request_class="deferrable"),
    )

    assert recovered_health.json()["providers"] == {"simulated": "healthy"}
    assert recovered_chat.status_code == 200
    assert recovered_chat.json()["request_class"] == "deferrable"
