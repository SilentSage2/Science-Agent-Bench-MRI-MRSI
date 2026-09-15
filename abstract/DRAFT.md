# Working abstract draft

Status: **PLANNED / NOT SUBMISSION-READY**. Bracketed text is an evidence dependency, not prose for submission.

<!-- ISMRM:TITLE:START -->
MR-AgentGuard: Failure-aware evaluation of scientific agents for MRI and MRSI under fixed budgets
<!-- ISMRM:TITLE:END -->

## Synopsis

<!-- ISMRM:SYNOPSIS:START -->
**Motivation:** Automated MR workflows can finish without errors while violating multi-coil acquisition physics or attenuating metabolites, risking false scientific conclusions.

**Goal(s):** Test whether agent control strategies detect or prevent silent MRI/MRSI invalidity under fixed budgets.

**Approach:** Compare five budget-auditable strategies on evaluator-isolated tasks spanning multi-coil undersampling/noise and spectral drift/template mismatch, using hidden physics/fidelity graders.

**Results:** PLANNED—no frozen primary outcomes exist. Development-only mechanism and calibration evidence is excluded from agent-effect inference.
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

**PLANNED primary study.** Two generated research-core candidates are implemented. Noisy multi-coil Cartesian MRI exposes zero-filled and regularized SENSE-CG reconstruction; hidden grading measures magnitude/gradient NRMSE and acquired-data residual. Complex MRSI exposes fixed or adaptive nuisance projection under frequency/phase drift, baseline and lineshape mismatch, and noise; hidden grading separately measures nuisance residual, metabolite retention, and whole-spectrum error. Naive, conventional, and evaluator-only oracle references calibrate each family. Nine generated development cases per family quantify naive-versus-conventional task separation without estimating agent effects. Public/challenge physics and MR-domain validation remain required. Policies receive versioned public inputs and typed observations, never clean anatomy, spectra, or generator parameters.

One pinned model snapshot will run the primary controller ablation: direct, self-debug, reactive, plan-only, and plan plus one bounded retry/replan. Conventional MR methods, a naive method, and an oracle calibrate each task without being misrepresented as agents. Conditions will share prompts where applicable, allowlisted research tools, token/cost/tool/time ceilings, seeds, and the digest-pinned network-disabled non-root executor. Plan-only versus reactive will isolate initial planning; retry/replan versus plan-only will isolate recovery. A blinded design-stage sensitivity analysis specifies 61 independent instances per family and two repetitions per condition (1,220 runs total); expert signoff, private manifest materialization, model/budget freeze, and spend authorization remain PLANNED.

Co-primary MR endpoints will be silent-invalidity prevention and recognition among technically completed runs. Prevention requires hidden scientific validity; recognition requires the final agent assessment to flag an invalid or uncertain result. MRI metrics will include magnitude and gradient NRMSE plus sampled multi-coil k-space residual. MRSI metrics will include nuisance suppression, metabolite-retention error, and robustness to frequency/phase drift and template mismatch. Secondary endpoints will include reproducibility, provider-reported tokens, dated cost, wall time, calls, retries, and policy violations. Repetitions will be averaged within instance-condition cells. Paired differences will use task instance as the resampling unit with a seeded task-family-stratified bootstrap for 95% intervals. Missing usage will not be imputed as zero. Exclusions and reruns will follow predeclared rules.

Runs will record code revision, dirty state, task/model/prompt/tool/container hashes, budgets, usage, seeds, hardware, transitions, actions, observations, artifacts, and grader output. Clean-checkout reproduction is validated for the development release; the private primary release manifest remains PLANNED until signed protocol freeze.

### Results

**PLANNED—NO REAL-MODEL PRIMARY RESULTS EXIST.** Development mechanism checks verified that MRI and MRSI outputs can complete normally with reproducible artifacts while failing hidden spatial-fidelity or nuisance/metabolite-retention criteria. These checks and the paid development checkout are excluded from controller-effect inference. [Insert eligible denominators, paired effects, 95% intervals, family-stratified outcomes, cost, missingness, and frozen `R-*` fact IDs only after the signed primary analysis.]

### Discussion

**PLANNED.** [Interpret effect magnitude and uncertainty rather than pass-count direction alone. Separate prevention from recognition and MRI from MRSI. Discuss null or adverse effects, cost/latency tradeoffs, recovery failures, and boundary cases. State limitations from generated tasks, one model snapshot, deterministic thresholds, provider alias drift, absent clinical validation, and the extent to which public/challenge validation supports—or refutes—the simulated mechanisms.]

### Conclusion

**PLANNED.** [Answer whether any controller component changed scientifically valid MRI/MRSI completion or recognition under fixed budgets, using the frozen paired estimate and interval. A null, harmful, or heterogeneous result is a valid conclusion. Do not generalize to patient care or models/tasks not evaluated.]
<!-- ISMRM:BODY:END -->

## References

**PLANNED.** Freeze numbered scientific references after the technical literature review. Format-guideline and example-proceedings links belong in `abstract/README.md`, not in the scientific reference list.
