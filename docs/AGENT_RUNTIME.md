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

The registry is a correctness boundary, not a security sandbox. `DockerContainerExecutor` now provides the separate execution boundary: digest-pinned image, no network, read-only inputs and runtime, run-scoped output, non-root identity, dropped capabilities, and process, CPU, memory, time, stream, file, and artifact limits. Its local integration suite exercises denial controls against a real Docker daemon.

The current reference task bindings intentionally call deterministic Python solvers in the host process because they contain repository-authored trusted code and exist only to validate orchestration. Model-authored code remains disabled. A future research tool becomes eligible only after its allowlisted entry point is wired through `DockerContainerExecutor`; availability of a plain subprocess is never an acceptable fallback.
