# MRI/MRSI agent runtime

`MRIScienceAgent` is the provider-neutral, single-agent A1 controller. It combines one model adapter, one frozen controller condition, an immutable tool registry, hard multidimensional budgets, the fail-closed state machine, append-only trajectories, and a deterministic evaluator.

## Conditions

- `direct`: one pre-observation method choice and validity commitment, with no post-observation model turn;
- `self_debug`: execution without an initial plan, followed by one required public-diagnostic-conditioned revision of a clean successful candidate; a typed failure may instead consume the same single retry allowance;
- `reactive`: execution without an initial plan, followed by one post-observation validity assessment and no revision;
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

The orchestration path is implemented and offline-tested across all five conditions, including direct precommit, successful-candidate self-debug revision, structured retry/replan, missing usage, disallowed tools, and budget exhaustion. The runtime rejects direct actions without a precommit, early self-debug finalization, and unchanged self-debug candidates. Fixed-path reference bindings carry all four development families through immutable run records. Separate MRI and MRSI research bindings expose bounded algorithm choices and hidden scientific graders through the same action/observation/trajectory schema.

The registry is a correctness boundary, not a security sandbox. `DockerContainerExecutor` now provides the separate execution boundary: digest-pinned image, no network, read-only inputs and runtime, run-scoped output, non-root identity, dropped capabilities, and process, CPU, memory, time, stream, file, and artifact limits. Its local integration suite exercises denial controls against a real Docker daemon.

Reference bindings intentionally call deterministic Python solvers in the host process because they exist only to validate orchestration. Research bindings call allowlisted repository-owned entry points through `DockerContainerExecutor`; the trusted host executor used by `research_dry_run` is explicitly labeled non-model plumbing validation. Model-authored arbitrary code remains disabled, and a plain subprocess is never an acceptable production fallback.
