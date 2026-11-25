# Self-Healing LLM Gateway

A learning project for building a gateway that routes text requests to hosted model APIs, recovers from provider failures, and respects a **$0 budget**. The eventual React dashboard will show what happened to each request.

**Current milestone:** the local simulation foundation is complete. It requires zero accounts, API keys, or model quota. The next milestone is live-provider normalization and routing through LiteLLM.

## Run the foundation

The project requires Python 3.12 or newer. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m uvicorn backend.app.main:app --reload
```

Check the service in another terminal:

```bash
curl --fail --silent http://127.0.0.1:8000/health

curl --fail --silent \
  -H 'content-type: application/json' \
  -d '{"messages":[{"role":"user","content":"Hello gateway"}],"request_class":"interactive"}' \
  http://127.0.0.1:8000/v1/chat/completions
```

Run the tests with:

```bash
.venv/bin/python -m pytest
```

The simulated adapter supports deterministic failure, recovery, and latency in tests without making a network request. Gateway settings define separate `interactive` and `deferrable` request classes plus provider preference, deadlines, attempt budgets, circuit-breaker thresholds, and latency budgets.

Live providers are disabled. See [the provider eligibility policy](docs/provider-policy.md) for the evidence required before one can receive traffic.

## Where things go

| Folder | Responsibility |
| --- | --- |
| [`backend/`](backend/README.md) | The FastAPI service, provider adapters, and routing decisions |
| [`frontend/`](frontend/README.md) | The React and Vite dashboard |
| [`tests/`](tests/README.md) | Tests with simulated providers, including failure and recovery |
| [`docs/`](docs/roadmap.md) | The build plan and notes explaining what we learned |

## Follow one request

`Client -> FastAPI gateway -> simulated provider -> gateway -> client`

The browser sends a prompt as JSON, a structured text format. FastAPI validates the request and asks the provider adapter for a response. The first adapter returns a fixed reply so you can inspect the whole exchange before adding a network call. A request ID lets you match the browser's response with the gateway's log.

Start with the [roadmap](docs/roadmap.md). Use the [GitHub guide](docs/github.md) for the initial push and a daily commit routine.
