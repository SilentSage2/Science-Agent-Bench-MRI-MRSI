# Working abstract draft

Status: **PLANNED / NOT SUBMISSION-READY**. Bracketed text is an evidence dependency, not prose for submission.

<!-- ISMRM:TITLE:START -->
Failure-aware planning for scientifically valid autonomous MRI/MRSI experiments under fixed budgets
<!-- ISMRM:TITLE:END -->

## Synopsis

<!-- ISMRM:SYNOPSIS:START -->
**Motivation:** Automated MR workflows can finish without errors while violating multi-coil acquisition physics or attenuating metabolites, risking false scientific conclusions.

**Goal(s):** Test whether agent control strategies detect or prevent silent MRI/MRSI invalidity under fixed budgets.

**Approach:** Compare five budget-auditable strategies on evaluator-isolated tasks spanning multi-coil undersampling/noise and spectral drift/template mismatch, using hidden physics/fidelity graders.

**Results:** PLANNED—no real-model comparison has run. The frozen analysis will report paired effects, 95% intervals, efficiency, and MR-specific failures.
<!-- ISMRM:SYNOPSIS:END -->

## Impact

<!-- ISMRM:IMPACT:START -->
PLANNED—The study will show whether agent controls can detect or prevent physically plausible but scientifically invalid MRI/MRSI outputs, helping MR researchers protect reconstruction and spectroscopy conclusions rather than relying on error-free execution alone.
<!-- ISMRM:IMPACT:END -->

## Main body

<!-- ISMRM:BODY:START -->
### Introduction

Automated tools and language-model agents can complete MRI or MR spectroscopic imaging (MRSI) workflows without raising an exception while returning scientifically misleading output. In MRI reconstruction, a plausible image may violate the acquired multi-coil forward model or lose spatial detail; in MRSI processing, strong water/lipid suppression may silently attenuate metabolites under frequency/phase drift or template mismatch. File creation and executable-code success do not protect MR conclusions from these failures. We ask whether agent control strategies detect or prevent such silent invalidity when model, task, tools, and budgets are fixed.

### Methods

**PLANNED primary study.** Four development-fixture families currently cover proton-MRS basis-model selection, MRSI water/lipid nuisance removal, undersampled Cartesian MRI reconstruction, and subject/session split-leakage audit. Before primary runs, MRI reconstruction and MRSI nuisance removal must be rebuilt as research-grade core tasks with realistic dimensions, noise/mismatch strata, meaningful algorithm choices, conventional MR baselines, and public/challenge-derived or literature-justified simulation evidence. The other families will remain secondary unless they pass the same gate. Hidden references will be accessible only to deterministic graders; policies will receive versioned public inputs and typed observations.

One pinned model snapshot will run the primary controller ablation: reactive, plan-only, and plan plus one bounded retry/replan. Budget-auditable direct generation and self-debug will provide competitive scientific-agent baselines; conventional MR methods, a naive method, and an oracle will calibrate each task without being misrepresented as agents. Conditions will share prompts where applicable, allowlisted research tools, token/cost/tool/time ceilings, seeds, and the digest-pinned network-disabled non-root executor. Plan-only versus reactive will isolate initial planning; retry/replan versus plan-only will isolate recovery. [PLANNED: use a blinded design-stage sensitivity analysis to set independent instance and repetition counts, then freeze model ID, prompts, tools, budgets, instance hashes, exclusions, and seeds before opening outcomes.]

Co-primary MR endpoints will be silent-invalidity prevention and recognition among technically completed runs. Prevention requires hidden scientific validity; recognition requires the final agent assessment to flag an invalid or uncertain result. MRI metrics will include magnitude and gradient NRMSE plus sampled multi-coil k-space residual. MRSI metrics will include nuisance suppression, metabolite-retention error, and robustness to frequency/phase drift and template mismatch. Secondary endpoints will include reproducibility, provider-reported tokens, dated cost, wall time, calls, retries, and policy violations. Repetitions will be averaged within instance-condition cells. Paired differences will use task instance as the resampling unit with a seeded task-family-stratified bootstrap for 95% intervals. Missing usage will not be imputed as zero. Exclusions and reruns will follow predeclared rules.

Runs will record code revision, dirty state, task/model/prompt/tool/container hashes, budgets, usage, seeds, hardware, transitions, actions, observations, artifacts, and grader output. [PLANNED: provide the single clean-environment reproduction command and release manifest after protocol freeze.]

### Results

**PLANNED—NO REAL-MODEL PRIMARY RESULTS EXIST.** A mechanism check confirmed that one zero-filled multi-coil reconstruction completed normally and produced valid artifacts yet failed hidden magnitude/gradient fidelity criteria; this endpoint validation is not a controller result. [Insert eligible run counts; paired invalidity prevention/recognition effects with 95% intervals; MRI/MRSI fidelity; efficiency; and prespecified failure counts exclusively from frozen `R-*` fact-map entries.]

### Discussion

**PLANNED.** [Interpret effect magnitude and uncertainty rather than pass-count direction alone. Discuss null or adverse effects, task-family heterogeneity, cost/latency tradeoffs, recovery failures, and boundary cases. State limitations from generated tasks, the sensitivity-justified but likely small instance set, one model snapshot, deterministic graders, and lack of clinical validation.]

### Conclusion

**PLANNED.** [Answer whether planning and bounded replan changed scientifically valid MRI/MRSI experiment completion under fixed budgets, using the frozen paired estimate and interval. Do not generalize to patient care or models/tasks not evaluated.]
<!-- ISMRM:BODY:END -->

## References

**PLANNED.** Freeze numbered scientific references after the technical literature review. Format-guideline and example-proceedings links belong in `abstract/README.md`, not in the scientific reference list.
