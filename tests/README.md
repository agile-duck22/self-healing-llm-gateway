# Tests

The foundation suite checks health reporting, valid simulated replies, malformed request validation, request deadlines, provider failure and recovery, request-class configuration, invalid resilience settings, and live-provider eligibility guardrails. It uses zero live model requests.

Run it from the repository root with:

```bash
.venv/bin/python -m pytest
```
