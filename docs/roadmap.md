# Build roadmap

| Milestone | Build | Check your understanding |
| --- | --- | --- |
| 1. Simulated request | FastAPI health and chat endpoints, then a React playground. Return a fixed response and a request ID. | Trace a prompt from the browser to the server and back. Find the request ID in both places. |
| 2. One live backend | Connect one verified free model. Require caller authentication, cap input and output, and reserve a small usage allowance before sending. | Explain where the key lives and what happens when the allowance runs out. |
| 3. Routing and visibility | Add eligible free models from the planned Groq, Gemini, and OpenRouter API backends. Add tenant and feature attribution, attempt logs, and a dashboard for health and usage. | Explain why a provider was picked and distinguish a provider attempt from a user request. |
| 4. Failover and recovery | Use a bounded attempt budget, a total deadline, and circuit breakers with recovery probes. Keep health, quotas, and breaker state in Redis once persistence is needed. | Simulate a failure, watch traffic move, and explain when the original backend becomes eligible again. |
| 5. Deferred jobs | Add a Redis-backed jobs endpoint with idempotency, leases, backoff, and expiry. | Submit the same job twice and recover it after a gateway restart. |
| 6. Hosted demo | Verify free hosting and storage limits. Host the dashboard and gateway, protect metrics and chaos controls, and record a controlled outage and recovery. | Report measured outcomes and explain how a sleeping host affects queued work. |

## Enforcing the $0 boundary

- Start in simulation. Confirm the live provider's current pricing and account limits before enabling a specific model. Recheck those terms when changing models or providers.
- Enable only explicitly verified free models and keep paid billing disabled where the service supports it. Store provider keys on the backend in ignored local environment files or the host's secret settings.
- Reserve usage before every outbound attempt. If pricing is unverified or the allowance cannot be confirmed, skip that provider. If all eligible providers are unavailable, return a clear error or defer eligible work once the queue exists.
- Use simulated failures for automated tests and chaos demonstrations. A content refusal ends the request. A timeout can trigger fallback within the attempt budget.
- Add shared storage, hosting, and monitoring only when the corresponding milestone needs them. Verify each service's free-plan behavior before deploying.

## First session

Before writing the endpoint, predict what `GET /health` will return when the server is running. Then send the request, stop the server, and try again. Write one or two sentences about the difference between an HTTP error response and a connection failure. That note can be your next meaningful commit.
