# MRI/MRSI agent runtime

`MRIScienceAgent` is the provider-neutral, single-agent A1 controller. It combines one model adapter, one frozen controller condition, an immutable tool registry, hard multidimensional budgets, the fail-closed state machine, append-only trajectories, and a deterministic evaluator.

## Conditions

- `reactive`: begin execution immediately and stop on a failed tool observation;
- `plan_only`: require one structured plan, then execute without retry;
- `plan_retry_replan`: require a plan and permit one typed, budgeted retry followed by one structured replan.

The condition changes control flow only. Model, task instances, prompts, action schemas, registered tools, evaluator, and budget ceilings must otherwise remain identical.

## Safety and accounting invariants

- A tool must be both registered and named in `TaskSpec.allowed_tools`.
- There is no dynamic import, arbitrary shell, or unknown-tool fallback.
- Every model and tool call reserves its worst-case budget before execution.
- Provider token usage is required; missing usage fails the run rather than becoming zero.
- Token price is a dated, frozen nanodollar-per-token input and is rounded up to integer microdollars.
- Usage above a reservation terminates as `budget_exceeded`.
- Invalid action kinds and disallowed tools fail closed.
- Run manifests never contain credentials; trajectories store validated actions, observations, usage, and model identifiers.
- Hidden evaluator references are supplied only to the evaluator closure and never enter policy input.

## Current boundary

The orchestration path is implemented and offline-tested across all three conditions, including retry recovery, missing usage, disallowed tools, and budget exhaustion. Fixed-path reference bindings now carry all four task families through model action, artifact creation, independent grading, and immutable run records. These bindings validate infrastructure only; research-grade tools must expose meaningful scientific choices rather than a reference answer.

The registry is a correctness boundary, not a security sandbox. Before any model-authored code is allowed, tool execution must move into the planned disposable, network-disabled, non-root container with read-only inputs, a run-scoped output mount, and hard operating-system resource limits.
