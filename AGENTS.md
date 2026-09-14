# Repository instructions

## Purpose

Science Agent Bench measures which agent control-loop components improve small scientific-computing tasks under fixed model, token, cost, tool, retry, and execution budgets.

## Scope

- Keep the benchmark agent-neutral and provider adapters replaceable.
- Preserve explicit typed interfaces for tasks, actions, observations, state, budgets, trajectories, executors, policies, and evaluators.
- Use generated or public data with recorded provenance and licenses.
- Treat model-authored code as untrusted. Never describe a subprocess wrapper as a secure sandbox.
- Do not add multi-agent coordination, persistent cross-task memory, a web UI, or unrestricted shell execution before A1 is complete.

## Research standards

- Compare reactive, plan-only, and plan-plus-retry/replan conditions under identical budgets.
- Freeze task instances, prompts, graders, tool schemas, model settings, and budgets before headline comparisons.
- Grade task success, scientific validity, reproducibility, efficiency, and policy violations separately.
- Keep hidden grader values outside policy-visible inputs and trajectories.
- Report paired outcomes and uncertainty; distinguish planned from executed results.

## Engineering standards

- Support Python 3.12 with a small typed standard-library core.
- Keep task specifications versioned data; do not hard-code task answers in runtime code.
- Fail closed on invalid state transitions, malformed records, budget exhaustion, and path violations.
- Write immutable run directories and append-only JSONL trajectories.
- Add tests for schemas, accounting, state transitions, serialization, artifact hashes, grader positive cases, and adversarial negative cases.
- Run formatting, linting, typing, unit tests, and an offline mock smoke test before merging.
- Never commit credentials, provider responses containing sensitive data, generated runs, private evaluator fixtures, datasets, or model artifacts.

