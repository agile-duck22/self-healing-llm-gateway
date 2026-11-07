# Self-Healing LLM Gateway

A learning project for building a gateway that routes text requests to hosted model APIs, recovers from provider failures, and respects a **$0 budget**. The eventual React dashboard will show what happened to each request.

**Current milestone:** repository scaffold. The first implementation milestone is a local simulated request that requires zero accounts, API keys, or model quota.

## Where things go

| Folder | Responsibility |
| --- | --- |
| [`backend/`](backend/README.md) | The FastAPI service, provider adapters, and routing decisions |
| [`frontend/`](frontend/README.md) | The React and Vite dashboard |
| [`tests/`](tests/README.md) | Tests with simulated providers, including failure and recovery |
| [`docs/`](docs/roadmap.md) | The build plan and notes explaining what we learned |

## Follow one request

`Browser -> FastAPI gateway -> simulated provider -> gateway -> browser`

The browser sends a prompt as JSON, a structured text format. FastAPI validates the request and asks the provider adapter for a response. The first adapter returns a fixed reply so you can inspect the whole exchange before adding a network call. A request ID lets you match the browser's response with the gateway's log.

Start with the [roadmap](docs/roadmap.md). Use the [GitHub guide](docs/github.md) for the initial push and a daily commit routine.
