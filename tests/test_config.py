from types import MappingProxyType

import pytest

from backend.app.config import (
    GatewaySettings,
    ProviderEligibility,
    RequestClass,
    RoutePolicy,
)


def test_default_settings_define_both_request_classes() -> None:
    settings = GatewaySettings.from_environment()

    assert set(settings.routes) == {
        RequestClass.INTERACTIVE,
        RequestClass.DEFERRABLE,
    }
    assert (
        settings.routes[RequestClass.INTERACTIVE].timeout_seconds
        < settings.routes[RequestClass.DEFERRABLE].timeout_seconds
    )
    assert settings.routes[RequestClass.INTERACTIVE].provider_preference == (
        "simulated",
    )


def test_live_provider_requires_all_eligibility_evidence() -> None:
    defaults = GatewaySettings.from_environment()
    settings = GatewaySettings(
        routes=defaults.routes,
        live_provider_evidence=MappingProxyType(
            {
                "verified": ProviderEligibility(
                    pricing_verified=True,
                    free_allowance_verified=True,
                    paid_billing_disabled=True,
                ),
                "unverified": ProviderEligibility(pricing_verified=True),
            }
        ),
    )

    assert settings.provider_is_eligible("simulated")
    assert settings.provider_is_eligible("verified")
    assert not settings.provider_is_eligible("unverified")
    assert not settings.provider_is_eligible("missing")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider_preference", ()),
        ("timeout_seconds", 0),
        ("attempt_budget", 0),
        ("breaker_error_threshold", 0),
        ("breaker_error_threshold", 1.1),
        ("latency_budget_ms", 0),
    ],
)
def test_invalid_route_policy_is_rejected(field: str, value: object) -> None:
    values = {
        "provider_preference": ("simulated",),
        "timeout_seconds": 1.0,
        "attempt_budget": 1,
        "breaker_error_threshold": 0.5,
        "latency_budget_ms": 1000,
    }
    values[field] = value

    with pytest.raises(ValueError):
        RoutePolicy(**values)
