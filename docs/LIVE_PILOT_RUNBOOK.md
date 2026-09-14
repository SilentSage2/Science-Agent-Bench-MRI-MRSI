# Credential-gated development pilot runbook

Status: **minimum checkout executed; revised design awaiting independent review**
Last pricing check: 2026-09-14

The project adapter passed a one-request paid smoke and a balanced 10-cell checkout was completed. See the [development pilot record](../experiments/real-model-development-pilot-v4/README.md). The existing deterministic replay remains plumbing validation only. Protocol v1.1 now makes direct pre-observation-only, reactive post-observation, and self-debug a required successful-candidate revision; adversarial trajectory tests pass. Do not expand the paid run until the revised mechanics, blinded design, MRSI spectral-axis abstraction, and candidate freeze receive the required independent review.

## Recommended checkout model

Use `gpt-5.6-terra` for the first development checkout because the official model catalog describes it as the balance of intelligence and cost, with Responses API and Structured Outputs support. The official price on 2026-09-14 is $2 per million input tokens and $12 per million output tokens. Re-check availability and pricing immediately before execution:

- [GPT-5.6 Terra model page](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
- [Responses API create reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)

The current official page does not expose a distinct dated Terra snapshot string. The development pilot may request `gpt-5.6-terra` and records the exact model returned by each response. A primary comparison must freeze an account-available immutable snapshot or explicitly disclose alias drift risk.

## Safe credential setup

Create a project-scoped API key with a small project spend limit. In a fresh terminal, enter it without putting the value in shell history:

```bash
read -s "OPENAI_API_KEY?OpenAI API key: "
export OPENAI_API_KEY
echo
```

Do not place the key in `.env`, JSON, TOML, commands, trajectories, or GitHub. Unset it after the run with `unset OPENAI_API_KEY`.

## Call and cost envelope

The two-instance checkout crosses two task families with five conditions: 10 run cells. The designed action paths use at most 30 model calls total; the fail-closed per-run ceiling permits at most 50 if a model behaves unexpectedly. At the frozen 12,000-input/3,000-output-token ceiling per run, the Terra hard cost bound is $0.60. A $1 aggregate breaker leaves room for rounding without authorizing a larger experiment.

The full 18-entry development manifest has 90 cells. Its intended paths use at most 270 calls; the absolute runtime ceiling is 450. Its token-budget cost bound is $5.40 at the stated Terra price. The 18 entries collapse to six declared dependence groups, so this is not a 90-sample or 18-independent-sample primary study.

## Reproducible checkout command

First build the image and copy the exact `sha256:...` ID printed by `docker image inspect`:

```bash
docker build --file docker/research.Dockerfile \
  --tag science-agent-bench-mri-research:local .
docker image inspect science-agent-bench-mri-research:local --format '{{.Id}}'
```

Then run exactly two manifest entries; the runner selects one MRI and one MRSI entry by balanced round-robin:

```bash
PYTHONPATH=src python3.12 -m science_agent.live_pilot \
  --manifest protocol/frozen_development_instances_v1.json \
  --output runs/credential-gated-development-pilot-v1 \
  --image sha256:REPLACE_WITH_LOCAL_IMAGE_ID \
  --model gpt-5.6-terra \
  --instance-limit 2 \
  --total-cost-ceiling-usd 1.00 \
  --acknowledge-paid-development-pilot
```

Do not interpret checkout differences among conditions. Before any primary run, balance family selection, freeze prompts and an immutable model identifier, complete MR-domain review, establish public/challenge validity, and replace the dependent development manifest with a sensitivity-justified independent-instance design.
