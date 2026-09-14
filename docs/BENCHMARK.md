# A1 benchmark protocol

## Hypotheses

Under identical model, MRI/MRSI task, tool, token, cost, execution, and retry budgets:

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

Co-primary MR outcomes are silent-invalidity prevention and recognition among technically completed runs. Prevention means the hidden physics/fidelity grader accepts the output; recognition means the agent flags an invalid or uncertain result rather than endorsing it. MRI continuous outcomes include magnitude and gradient NRMSE and sampled multi-coil k-space residual. MRSI outcomes will include nuisance suppression, metabolite-retention error, and robustness to frequency/phase drift and template mismatch. Secondary outcomes are reproducibility, policy violations, failure recovery, tokens, estimated cost, tool calls, retries, and wall time.

Report every task instance and component metric rather than one opaque composite score. Technical completion, hidden scientific validity, and agent recognition remain separate denominators so an error-free trajectory cannot masquerade as valid MR science. The MVP publishes raw paired outcomes; paired bootstrap confidence intervals are exploratory until there are enough independent instances. Harness failures are reported separately and excluded from model-success denominators.

## Tasks and splits

The catalog describes seven possible CPU-compatible families, but A1 targets two depth-qualified cores: multi-coil MRI reconstruction and complex-MRSI nuisance removal. Other families remain diagnostics unless they independently pass the same evidence gate; they will not be added merely to inflate task count. A blinded sensitivity analysis now specifies 61 independent instances per core family and two repetitions per condition. Expert review, private materialization, and the final generators/schemas/graders/baselines/input-hash freeze must precede the primary comparison.

Tasks evaluate computational research behavior only. They do not request diagnosis, prognosis, treatment selection, or patient-facing interpretation.

The deterministic mock policy is the CI oracle. The first replaceable real-model adapter is implemented and has completed a five-condition development checkout, but A1 cannot make a result claim until an independently sized, frozen comparison passes protocol and domain review. Provider comparison is not an A1 hypothesis.

## Run record

Every immutable run records Git revision and dirty state, resolved task and condition, model adapter and parameters, prompt and tool hashes, environment and container digest, dependency lock, seeds, hardware, timings, budgets and usage, input/output hashes, every state transition, every action and observation, grader version, and separate outcome metrics.

Secrets, authorization headers, hidden references, and private evaluator parameters must never enter policy-visible state or trajectories. Missing provider usage is recorded as unknown and prevents cost-normalized claims.

## Compute ceiling

- Unit and mock integration tests run offline on CPU.
- One task receives at most 60 seconds, 1 GiB RAM, 64 processes, 1 MiB artifacts, and 256 KiB captured output.
- The complete mock suite finishes within 10 minutes on a laptop CPU.
- A pre-freeze pilot is capped at 100 runs and USD 30. The primary run/cost ceiling is set only after sensitivity and per-run-cost measurements; if it is unaffordable, the claim narrows instead of underpowering a confirmatory comparison.

## A1 completion gate

A1 requires at least two research-grade core MR families with conventional/naive/oracle references, sensitivity-justified held-out instances, identical-budget execution of direct, self-debug, reactive, plan-only, and bounded-replan conditions, a green offline mock suite, complete trajectories and artifact hashes, fail-closed budget/state/path tests, tested container denial controls, one frozen real-model comparison, MR-domain review, and a README containing actual paired effects, uncertainty, costs, failures, architecture, and exact reproduction commands. Additional families do not count toward A1 merely because toy fixtures exist.
