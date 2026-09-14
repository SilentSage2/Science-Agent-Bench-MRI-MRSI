# Working abstract draft

Status: **PLANNED / NOT SUBMISSION-READY**. Bracketed text is an evidence dependency, not prose for submission.

<!-- ISMRM:TITLE:START -->
Failure-aware planning for scientifically valid autonomous MRI/MRSI experiments under fixed budgets
<!-- ISMRM:TITLE:END -->

## Synopsis

<!-- ISMRM:SYNOPSIS:START -->
**Motivation:** Autonomous agents may accelerate MRI and spectroscopic-imaging computation, but fluent outputs can conceal invalid science.

**Goal(s):** Test whether structured planning and one bounded replan change scientifically valid completion under fixed budgets.

**Approach:** Compare budget-auditable direct, self-debug, reactive, plan-only, and bounded-replan conditions on evaluator-isolated MRI/MRSI tasks with realistic stressors, deterministic domain graders, and isolated execution.

**Results:** PLANNED—no real-model comparison has run. The frozen analysis will report paired effects, 95% intervals, efficiency, and MR-specific failures.
<!-- ISMRM:SYNOPSIS:END -->

## Impact

<!-- ISMRM:IMPACT:START -->
PLANNED—If completed, this study will show whether planning and bounded recovery make autonomous MRI/MRSI computation more scientifically reliable under fixed budgets, helping MR researchers distinguish useful agent control from added cost or failure.
<!-- ISMRM:IMPACT:END -->

## Main body

<!-- ISMRM:BODY:START -->
### Introduction

Autonomous language-model agents can coordinate computational experiments, yet task completion does not ensure scientifically valid MRI or MR spectroscopic imaging (MRSI) output. Errors such as acquired-k-space inconsistency, metabolite attenuation, unsupported spectral-model selection, and subject leakage may remain hidden behind plausible reports. We ask whether structured planning and one failure-aware replan change valid completion relative to reactive execution when the model, tasks, tools, and budgets are fixed.

### Methods

**PLANNED primary study.** Four development-fixture families currently cover proton-MRS basis-model selection, MRSI water/lipid nuisance removal, undersampled Cartesian MRI reconstruction, and subject/session split-leakage audit. Before primary runs, MRI reconstruction and MRSI nuisance removal must be rebuilt as research-grade core tasks with realistic dimensions, noise/mismatch strata, meaningful algorithm choices, conventional MR baselines, and public/challenge-derived or literature-justified simulation evidence. The other families will remain secondary unless they pass the same gate. Hidden references will be accessible only to deterministic graders; policies will receive versioned public inputs and typed observations.

One pinned model snapshot will run the primary controller ablation: reactive, plan-only, and plan plus one bounded retry/replan. Budget-auditable direct generation and self-debug will provide competitive scientific-agent baselines; conventional MR methods, a naive method, and an oracle will calibrate each task without being misrepresented as agents. Conditions will share prompts where applicable, allowlisted research tools, token/cost/tool/time ceilings, seeds, and the digest-pinned network-disabled non-root executor. Plan-only versus reactive will isolate initial planning; retry/replan versus plan-only will isolate recovery. [PLANNED: use a blinded design-stage sensitivity analysis to set independent instance and repetition counts, then freeze model ID, prompts, tools, budgets, instance hashes, exclusions, and seeds before opening outcomes.]

The primary endpoint will be deterministic scientific-validity completion. Secondary endpoints will include artifact completion, reproducibility, provider-reported tokens, dated estimated cost, wall time, tool calls, retries, and policy violations. Repetitions will be averaged within instance-condition cells. Paired controller differences will use task instance as the resampling unit with a seeded 10,000-resample task-family-stratified cluster bootstrap for 95% intervals; an exact paired randomization sensitivity analysis will be used if its frozen assumptions are met. Missing usage will not be imputed as zero. Exclusions and reruns will follow predeclared rules. A separate injected-failure subset will test recovery and will not be pooled into the primary endpoint.

Runs will record code revision, dirty state, task/model/prompt/tool/container hashes, budgets, usage, seeds, hardware, transitions, actions, observations, artifacts, and grader output. [PLANNED: provide the single clean-environment reproduction command and release manifest after protocol freeze.]

### Results

**PLANNED—NO PRIMARY RESULTS EXIST.** [Insert completed and eligible run counts; paired scientific-validity estimates with 95% intervals; task-family effects; efficiency and policy-violation results; injected-failure recovery; and prespecified failure-taxonomy counts exclusively from frozen `R-*` fact-map entries. Do not insert scripted-smoke pass rates here.]

### Discussion

**PLANNED.** [Interpret effect magnitude and uncertainty rather than pass-count direction alone. Discuss null or adverse effects, task-family heterogeneity, cost/latency tradeoffs, recovery failures, and boundary cases. State limitations from generated tasks, the sensitivity-justified but likely small instance set, one model snapshot, deterministic graders, and lack of clinical validation.]

### Conclusion

**PLANNED.** [Answer whether planning and bounded replan changed scientifically valid MRI/MRSI experiment completion under fixed budgets, using the frozen paired estimate and interval. Do not generalize to patient care or models/tasks not evaluated.]
<!-- ISMRM:BODY:END -->

## References

**PLANNED.** Freeze numbered scientific references after the technical literature review. Format-guideline and example-proceedings links belong in `abstract/README.md`, not in the scientific reference list.
