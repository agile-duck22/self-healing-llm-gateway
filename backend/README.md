# Backend

FastAPI will receive requests and return JSON. Start with a health endpoint and one non-streaming chat request. Put the API entry point and request schemas in [`app/`](app/README.md).

Add a provider adapter when the first chat endpoint needs one. Keep routing, retry limits, and quota decisions in gateway code. LiteLLM can translate requests for live providers later.
