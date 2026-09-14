# A1 benchmark protocol

## Hypotheses

Under identical model, task, tool, token, cost, execution, and retry budgets:

1. a structured initial plan improves valid task completion over a reactive loop;
2. typed retry and one bounded replan recover execution failures more efficiently than repetition;
3. any completion gain remains after accounting for tokens, tool calls, cost, and wall time.

The hypotheses fail if richer control does not improve paired outcomes or if the apparent gain disappears under the fixed-budget comparison.

## Conditions

| Condition | Planning | Failure handling | Replanning |
|---|---|---|---|
| Reactive | None | Stop on terminal error | None |
| Plan-only | One structured initial plan | Stop on terminal error | None |
| Plan + retry/replan | One structured initial plan | One typed retry | Once after recoverable failure |

Conditions share frozen task instances, task prompts, model settings, tool schemas, execution environment, and hard budgets. Minimal condition-specific controller instructions are versioned and published.

## Outcomes

Primary outcomes are task success, scientific validity, and reproducibility. Secondary outcomes are valid-artifact rate, policy-violation rate, failure recovery, and tokens, estimated cost, tool calls, retries, and wall time per successful task.

Report every task instance and macro averages rather than one opaque composite score. The MVP publishes raw paired outcomes; paired bootstrap confidence intervals are exploratory until there are enough independent instances. Harness failures are reported separately and excluded from model-success denominators.

## Tasks and splits

Seven generated CPU-only families cover linear-model audit, decay estimation, numerical convergence, spectral peak recovery, two-sample simulation, leakage detection, and competing ODE models. Each begins with two public development and three evaluator-isolated held-out instances. Generators, schemas, grader versions, and input hashes are frozen before a real-model comparison.

The deterministic mock policy is the CI oracle. At least one replaceable real-model adapter must complete all three experimental conditions before A1 makes a result claim. Provider comparison is not an A1 hypothesis.

## Run record

Every immutable run records Git revision and dirty state, resolved task and condition, model adapter and parameters, prompt and tool hashes, environment and container digest, dependency lock, seeds, hardware, timings, budgets and usage, input/output hashes, every state transition, every action and observation, grader version, and separate outcome metrics.

Secrets, authorization headers, hidden references, and private evaluator parameters must never enter policy-visible state or trajectories. Missing provider usage is recorded as unknown and prevents cost-normalized claims.

## Compute ceiling

- Unit and mock integration tests run offline on CPU.
- One task receives at most 60 seconds, 1 GiB RAM, 64 processes, 1 MiB artifacts, and 256 KiB captured output.
- The complete mock suite finishes within 10 minutes on a laptop CPU.
- The first real-model comparison is capped at 100 runs and USD 30.

## A1 completion gate

A1 requires versioned contracts, deterministic graders and held-out instances for all seven families, a green offline mock suite, identical-budget execution of all three conditions, complete trajectories and artifact hashes, fail-closed budget/state/path tests, tested container denial controls, one frozen real-model comparison, and a README containing actual paired results, costs, failures, architecture, and exact reproduction commands.

