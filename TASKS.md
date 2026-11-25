# Self-Healing LLM Gateway Tasks

**Stack:** Python, LiteLLM, FastAPI, Redis, Prometheus, and Grafana
**Estimated build time:** 2 to 3 weeks part time

## Project outcome

- [ ] Keep traffic flowing while a provider is deliberately degraded.
- [ ] Show the provider failure, circuit-breaker trip, reroute, and automatic recovery on a live dashboard.
- [ ] Attribute usage and cost by tenant and feature.
- [ ] Measure availability during simulated outages so the final resume claim uses a real value.

## Foundation: Local simulation and guardrails

- [x] Add a FastAPI application entry point.
- [x] Add `GET /health` and verify its response.
- [x] Add a simulated chat provider that requires no account, key, quota, or live model call.
- [x] Test valid requests, malformed requests, timeouts, provider errors, and recovery with simulated providers.
- [x] Define request classes, beginning with `interactive` and `deferrable`.
- [x] Define configuration for provider preference lists, timeouts, attempt budgets, breaker thresholds, and latency budgets.
- [x] Keep provider credentials on the backend in ignored local environment files or deployment secret settings.
- [x] Require current pricing and free-tier verification before enabling any live model.
- [x] Require paid billing to be disabled where the provider supports it.
- [x] Enforce that providers with unverified pricing or allowance cannot receive traffic.

## Phase 1: Route every model call through one service

### OpenAI-compatible gateway

- [ ] Add `POST /v1/chat/completions` with an OpenAI-compatible request and response shape.
- [ ] Validate prompts, model selection, request class, and output limits at the API boundary.
- [ ] Require `tenant`, `feature`, and `request_id` metadata on every request.
- [ ] Preserve the request ID through gateway logs, provider attempts, metrics, and responses.
- [ ] Return structured errors that distinguish gateway failures from provider failures.
- [ ] Document the minimal client change needed to use the gateway as an OpenAI-compatible base URL.

### Provider normalization and routing

- [ ] Integrate LiteLLM to normalize provider request and response differences.
- [ ] Configure at least three verified providers so failover has multiple destinations.
- [ ] Start with eligible free models from Groq, Gemini, and OpenRouter after checking their current terms.
- [ ] Define provider preference lists per request class.
- [ ] Record why each provider was selected or skipped.
- [ ] Distinguish the user request from every individual provider attempt in stored data and logs.
- [ ] Reserve usage allowance before each outbound attempt.
- [ ] Cap input and output tokens for every live request.
- [ ] Require caller authentication before enabling live providers.

### Phase 1 verification

- [ ] Send an OpenAI-compatible request through the gateway and receive a normalized response.
- [ ] Trace one request ID from the client through all provider attempts and back to the response.
- [ ] Explain where provider keys live and what happens when an allowance is exhausted.
- [ ] Verify an ineligible or over-budget provider is skipped without receiving traffic.

## Phase 2: Track health per provider

### Health model

- [ ] Maintain a rolling health window for every provider.
- [ ] Track request count, success rate, and latency samples in the window.
- [ ] Calculate p50, p95, and p99 latency per provider.
- [ ] Define a provider error taxonomy covering rate limits, timeouts, server errors, content filters, and authentication failures.
- [ ] Treat content refusals as terminal request outcomes rather than retryable infrastructure failures.
- [ ] Make retry eligibility explicit for every error category.

### Redis persistence

- [ ] Store health counters and rolling-window data in Redis.
- [ ] Use a sliding-window design with bounded retention and cleanup.
- [ ] Store quota and later circuit state in Redis when shared persistence is required.
- [ ] Verify a gateway restart does not reset the provider-health view.
- [ ] Test concurrent updates so health data remains consistent across gateway workers.

### Prometheus instrumentation

- [ ] Add a Prometheus `/metrics` endpoint before implementing automatic failover.
- [ ] Export request totals and latency histograms by provider and outcome.
- [ ] Export error totals by provider and error category.
- [ ] Export provider-attempt, failover, queue, circuit-state, token-usage, and estimated-cost metrics.
- [ ] Keep metric labels bounded and exclude request IDs, prompts, and other high-cardinality or sensitive values.
- [ ] Verify Prometheus can scrape the gateway and that a simulated request changes the expected metrics.

## Phase 3: Fail over automatically

### Circuit breakers

- [ ] Implement an independent circuit breaker for every provider.
- [ ] Support `closed`, `open`, and `half_open` states.
- [ ] Open the breaker when error rate exceeds its threshold within the rolling window.
- [ ] Open the breaker when p95 latency exceeds the configured budget.
- [ ] Define minimum sample sizes and cooldown periods to avoid unstable breaker transitions.
- [ ] Persist or coordinate breaker state across gateway workers when Redis-backed operation is enabled.
- [ ] Record every transition with its trigger, provider, timestamp, and request class.

### Routing and recovery

- [ ] Route around open circuits using the preference list for the request class.
- [ ] Use different preference lists for cheap classification and long-form generation.
- [ ] Enforce a bounded provider-attempt budget and total request deadline.
- [ ] Return a clear error for interactive requests when no eligible provider remains.
- [ ] Send a small, configurable share of traffic to a recovering provider while its circuit is half open.
- [ ] Close the breaker after sufficient successful probes.
- [ ] Reopen the breaker immediately after a failed half-open probe.
- [ ] Test recovery so the original provider becomes eligible without manual intervention.

### Hedged requests

- [ ] Add hedged requests for explicitly configured latency-sensitive request classes.
- [ ] Start the second provider only after the configured delay.
- [ ] Return the first successful response and cancel or disregard the losing request safely.
- [ ] Keep hedged attempts inside the total deadline and attempt budget.
- [ ] Record both attempts and their cost even when one result is discarded.
- [ ] Document that hedging can roughly double provider spend for hedged calls.

### Phase 3 verification

- [ ] Simulate rate limits, timeouts, server errors, slow responses, authentication errors, and content refusals.
- [ ] Verify only retryable failures trigger fallback.
- [ ] Degrade one provider and verify the breaker opens and traffic moves to the correct fallback.
- [ ] Recover the provider and verify half-open probes close the breaker automatically.
- [ ] Verify request deadlines and attempt limits prevent retry storms.

## Phase 4: Queue and retry deferrable work

### API behavior

- [ ] Require callers to classify work as `interactive` or `deferrable` at the API boundary.
- [ ] Make interactive requests fail fast when no provider can meet their deadline.
- [ ] Return a job identifier when deferrable work is queued.
- [ ] Add job-status and result endpoints with clear terminal states.

### Redis queue

- [ ] Queue deferrable work in Redis when every eligible provider is degraded.
- [ ] Retry with exponential backoff and jitter.
- [ ] Bound retry count, job age, and queue retention.
- [ ] Add leases so work can be recovered after a worker interruption.
- [ ] Add idempotency keys and enforce them before executing side effects.
- [ ] Ensure retries cannot duplicate a completed side effect.
- [ ] Reserve provider allowance again before every queued outbound attempt.
- [ ] Define dead-letter or terminal failure behavior for exhausted jobs.

### Phase 4 verification

- [ ] Submit the same idempotency key twice and verify work executes once.
- [ ] Interrupt a worker and verify the leased job is recovered safely.
- [ ] Restart the gateway and verify queued work and job status survive.
- [ ] Degrade every provider and verify interactive requests fail while deferrable work queues.
- [ ] Recover a provider and verify queued work drains with bounded retry traffic.

## Phase 5: Observe it, break it, and demonstrate recovery

### Grafana dashboard

- [ ] Provision Prometheus as the Grafana data source.
- [ ] Add requests-per-second panels grouped by provider.
- [ ] Add provider error-rate panels.
- [ ] Add p50, p95, and p99 latency panels.
- [ ] Add a circuit-state timeline.
- [ ] Add failover-event panels or annotations.
- [ ] Add queue-depth and queue-age panels.
- [ ] Add estimated cost-per-hour panels grouped by tenant and feature.
- [ ] Add request volume and token usage grouped by tenant and feature.
- [ ] Verify every dashboard panel changes during a controlled test.

### Chaos testing

- [ ] Add a protected chaos endpoint or proxy that can inject provider errors and latency on demand.
- [ ] Scope chaos controls by provider and failure type.
- [ ] Protect chaos controls and operational metrics from unauthorized callers.
- [ ] Ensure chaos mode is disabled by default and visibly reported when active.
- [ ] Automate a scenario covering healthy traffic, degradation, breaker trip, reroute, half-open probes, and recovery.
- [ ] Measure availability, error rate, latency, failover time, recovery time, queue behavior, and estimated cost during the scenario.

### Demo and documentation

- [ ] Record a 90-second screen capture showing healthy traffic.
- [ ] Degrade a provider during the recording.
- [ ] Show its circuit opening and traffic rerouting on the dashboard.
- [ ] Show half-open probes and the circuit closing after recovery.
- [ ] Put the demo video at the top of the README.
- [ ] Add an architecture diagram and describe the request, metrics, and recovery flows.
- [ ] Document local startup, configuration, provider setup, testing, and the chaos demo.
- [ ] Document measured results and the assumptions behind estimated provider costs.
- [ ] Explain how sleeping hosts affect queued work if the demo uses free hosting.

## Definition of done

- [ ] A provider can be degraded live while traffic continues through eligible providers.
- [ ] The dashboard shows the degradation, breaker trip, reroute, half-open probes, and automatic recovery.
- [ ] Every request has tenant, feature, and request ID metadata.
- [ ] Usage and estimated cost are attributable by tenant and feature.
- [ ] Provider health persists across gateway restarts.
- [ ] Deferrable work survives a complete provider outage without duplicate side effects.
- [ ] Automated tests cover breaker transitions, routing, retry eligibility, deadlines, idempotency, and recovery.
- [ ] The 90-second demo and measured availability result are published in the README.

## Resume evidence

- [ ] Replace `X` with the measured result: “Built an LLM gateway with per-provider circuit breaking and automatic failover; sustained X% availability through simulated provider outages with per-tenant cost attribution.”
- [ ] Keep the load profile, outage duration, provider mix, and measurement method needed to defend the result in an interview.

## Review checklist for common failure modes

- [ ] Cost attribution exists for both tenant and feature.
- [ ] Retries and queued jobs cannot repeat non-idempotent side effects.
- [ ] Every circuit breaker has a tested half-open recovery path.
- [ ] The dashboard is backed by a repeatable chaos test.
- [ ] Error categories drive explicit retry behavior instead of treating every failure alike.
- [ ] Failover is bounded by attempt limits, deadlines, quotas, and cost controls.

## Stretch goals

- [ ] Add a semantic cache with safe cache keys, tenant isolation, expiry, and cache metrics.
- [ ] Add a model-tiering router that sends easier requests to smaller models.
- [ ] Add per-tenant rate limits and spending budgets.
- [ ] Add request logging with PII detection and redaction.

## First session

- [ ] Predict the response from `GET /health` before starting the server.
- [ ] Start the server and send the health request.
- [ ] Stop the server and send the request again.
- [ ] Write one or two sentences explaining the difference between an HTTP error response and a connection failure.
