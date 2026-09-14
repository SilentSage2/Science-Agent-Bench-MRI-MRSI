# Model adapters

The benchmark policy depends on the `ModelAdapter` protocol rather than a provider SDK. A model request contains only versioned instructions, policy-visible input, a hard output-token ceiling, and the JSON Schema for the next `Action`. A result contains the validated action, provider/model identifiers, response ID, and provider-reported token usage.

## OpenAI Responses adapter

`OpenAIResponsesAdapter` calls `POST /v1/responses` using the standard library. It requests strict JSON Schema output, sets `store` to `false`, applies the declared `max_output_tokens`, and rejects incomplete, malformed, or contract-invalid responses. The request transport is injectable, so CI exercises the complete serialization and parsing boundary without network access or credentials.

Create the adapter at the application boundary:

```python
from science_agent import OpenAIResponsesAdapter

adapter = OpenAIResponsesAdapter.from_env(model="YOUR_FROZEN_MODEL_ID")
```

Set `OPENAI_API_KEY` only in the process environment. Never place it in configs, trajectories, run metadata, shell history, or committed files. The adapter does not calculate price: experiments must freeze a dated provider-pricing snapshot separately, then convert reported usage to integer microdollars. Missing usage remains unknown rather than being treated as zero.

The adapter is implemented and offline-tested, including nullable strict-schema fields that are removed before tool validation. A paid adapter smoke and two-instance development checkout have run, but no frozen research comparison exists. The [live pilot runbook](LIVE_PILOT_RUNBOOK.md) defines the credential boundary, current official price snapshot, call/cost envelope, aggregate breaker, and exact checkout command.

The request and response fields follow the official [OpenAI Responses API reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/create).
