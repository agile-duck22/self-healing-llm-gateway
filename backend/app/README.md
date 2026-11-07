# Gateway application

Start with `main.py` for the FastAPI application. Add `GET /health` so you can verify the server is responding. Then add `POST /v1/chat/completions` with one validated request shape and a simulated reply. Split endpoints, providers, and routing into modules as each responsibility grows.
