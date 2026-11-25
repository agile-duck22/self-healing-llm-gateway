# Gateway application

`main.py` exposes the FastAPI application, `config.py` defines request classes and resilience policies, `gateway.py` enforces routing and deadlines, and `providers/` contains provider adapters.

The current `SimulatedProvider` performs no network calls. It can inject latency, fail, and recover deterministically for tests. Live adapters will be added only after their pricing, free allowance, and billing controls satisfy the documented provider eligibility policy.
