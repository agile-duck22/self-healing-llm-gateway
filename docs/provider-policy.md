# Provider eligibility policy

The foundation is simulation-only. It does not configure, call, or require credentials for a live model provider.

A live provider is eligible for routing only after all three facts are recorded in gateway configuration:

1. Its current model pricing has been checked.
2. Its free allowance or zero-cost boundary has been checked.
3. Paid billing is disabled for the account where the provider supports that control.

Missing evidence makes the provider ineligible. The gateway also reserves allowance before each live attempt once live adapters are implemented. Provider terms change, so the evidence must be reviewed when a model or provider configuration changes.

| Provider | Pricing verified | Free allowance verified | Paid billing disabled | Enabled |
| --- | --- | --- | --- | --- |
| Simulated | Not applicable | Not applicable | Not applicable | Yes |
| Groq | No | No | No | No |
| Gemini | No | No | No | No |
| OpenRouter | No | No | No | No |
