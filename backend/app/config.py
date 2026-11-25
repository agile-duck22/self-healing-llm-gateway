"""Typed gateway configuration and provider eligibility guardrails."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping


class RequestClass(StrEnum):
    """Workload classes with different latency and delivery expectations."""

    INTERACTIVE = "interactive"
    DEFERRABLE = "deferrable"


@dataclass(frozen=True)
class RoutePolicy:
    """Routing and resilience limits for one request class."""

    provider_preference: tuple[str, ...]
    timeout_seconds: float
    attempt_budget: int
    breaker_error_threshold: float
    latency_budget_ms: int

    def __post_init__(self) -> None:
        if not self.provider_preference:
            raise ValueError("provider_preference must contain at least one provider")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.attempt_budget < 1:
            raise ValueError("attempt_budget must be at least one")
        if not 0 < self.breaker_error_threshold <= 1:
            raise ValueError("breaker_error_threshold must be in the range (0, 1]")
        if self.latency_budget_ms < 1:
            raise ValueError("latency_budget_ms must be positive")


@dataclass(frozen=True)
class ProviderEligibility:
    """Evidence required before the gateway may route to a live provider."""

    pricing_verified: bool = False
    free_allowance_verified: bool = False
    paid_billing_disabled: bool = False

    @property
    def eligible(self) -> bool:
        return (
            self.pricing_verified
            and self.free_allowance_verified
            and self.paid_billing_disabled
        )


@dataclass(frozen=True)
class GatewaySettings:
    """Application settings with safe, simulation-only defaults."""

    routes: Mapping[RequestClass, RoutePolicy]
    live_provider_evidence: Mapping[str, ProviderEligibility] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        missing = set(RequestClass) - set(self.routes)
        if missing:
            names = ", ".join(sorted(request_class.value for request_class in missing))
            raise ValueError(f"missing route policies for: {names}")

    def provider_is_eligible(self, provider_name: str) -> bool:
        if provider_name == "simulated":
            return True
        evidence = self.live_provider_evidence.get(provider_name)
        return evidence is not None and evidence.eligible

    @classmethod
    def from_environment(cls) -> GatewaySettings:
        attempt_budget = _read_int("GATEWAY_ATTEMPT_BUDGET", default=1)
        error_threshold = _read_float(
            "GATEWAY_BREAKER_ERROR_THRESHOLD", default=0.5
        )
        latency_budget_ms = _read_int("GATEWAY_LATENCY_BUDGET_MS", default=1000)

        shared = {
            "provider_preference": ("simulated",),
            "attempt_budget": attempt_budget,
            "breaker_error_threshold": error_threshold,
            "latency_budget_ms": latency_budget_ms,
        }
        routes = MappingProxyType(
            {
                RequestClass.INTERACTIVE: RoutePolicy(
                    timeout_seconds=_read_float(
                        "GATEWAY_INTERACTIVE_TIMEOUT_SECONDS", default=2.0
                    ),
                    **shared,
                ),
                RequestClass.DEFERRABLE: RoutePolicy(
                    timeout_seconds=_read_float(
                        "GATEWAY_DEFERRABLE_TIMEOUT_SECONDS", default=10.0
                    ),
                    **shared,
                ),
            }
        )
        return cls(routes=routes)


def _read_float(name: str, *, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return float(raw_value)
    except ValueError as error:
        raise ValueError(f"{name} must be a number") from error


def _read_int(name: str, *, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error
