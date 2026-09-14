# Cross-artifact fact map

This registry prevents the abstract, figures, tables, captions, and README from drifting apart. `FROZEN-RESULT` rows are created only by the locked analysis pipeline.

| Fact ID | State | Fact | Source of truth | Allowed use |
|---|---|---|---|---|
| I-001 | IMPLEMENTED | Four deterministic task families exist: MRS basis selection, MRSI nuisance removal, MRI/MRSI leakage audit, and Cartesian MRI reconstruction | task specs, graders, tests | Methods; Figures 1–2 |
| I-002 | IMPLEMENTED | Direct, self-debug, reactive, plan-only, and bounded retry/replan paths exist behind one provider-neutral interface | agent runtime and deterministic dry-run tests | Methods; Figure 1 |
| I-003 | IMPLEMENTED | A digest-pinned, network-disabled, non-root Docker boundary with resource and artifact limits exists | container executor and denial tests | Methods; Figure 1 |
| I-004 | IMPLEMENTED | A noisy multi-coil Cartesian MRI candidate provides variable-density undersampling, complex coil sensitivities, zero-fill/SENSE-CG/oracle references, and hidden magnitude/gradient/data-residual grading | research MRI module and tests | Methods; Figure 2 |
| I-005 | IMPLEMENTED | A complex MRSI candidate provides frequency/phase drift, baseline/lineshape mismatch, noise, fixed/adaptive/oracle references, and hidden nuisance/retention/spectral grading | research MRSI module and tests | Methods; Figure 2 |
| V-001 | VALIDATED-INFRASTRUCTURE | Scripted reference runs pass all controller/task combinations | committed smoke summaries | Repository status only; never scientific Results |
| V-002 | VALIDATED-INFRASTRUCTURE | One containerized zero-fill case completed technically but failed hidden magnitude/gradient validity checks | MRI silent-invalidity endpoint record | Motivation/Methods mechanism example only; never controller prevalence/effect |
| V-003 | VALIDATED-INFRASTRUCTURE | One fixed-template complex-MRSI case completed technically but failed hidden nuisance, metabolite-retention, and spectral checks | MRSI silent-invalidity endpoint record | Motivation/Methods mechanism example only; never controller prevalence/effect |
| V-004 | DEVELOPMENT-PILOT | A two-instance, five-condition paid checkout reached hidden grading in 10/10 cells and exposed four unrecognized silently invalid MRI outputs, but cannot estimate controller effects | real-model development pilot v4 | Repository status and design refinement only; prohibited from abstract Results/Figures 3–5 |
| P-001 | PLANNED | Evaluator-isolated held-out set sized by blinded sensitivity analysis | design-stage simulation and frozen instance manifest not yet created | Methods future tense only |
| P-002 | PLANNED | One pinned model; direct, self-debug, reactive, plan-only, and bounded-replan conditions; repetition count and primary run total | protocol and sample size awaiting freeze | Approach/Methods future tense only |
| P-004 | PLANNED | Primary paired validity effects and 95% intervals | no primary runs | Synopsis Results, Results, Conclusion, Figure 3 only after freeze |
| P-005 | PLANNED | Token/cost/time tradeoffs and injected-failure recovery | no primary/failure runs | Results, Discussion, Figure 4 only after freeze |
| P-006 | PLANNED | Prespecified MR success/boundary/failure taxonomy | no frozen failure index | Results, Discussion, Figure 5 only after freeze |

At freeze, replace—not silently edit—`P-004` through `P-006` with new immutable `R-*` rows containing exact analysis keys, denominators, estimates, intervals, and source hashes.

## Experiment-to-package traceability

| Frozen experiment output | Synopsis/Impact | Main body/table | Figure |
|---|---|---|---|
| Protocol, task and model manifests | Approach | Methods | Figure 1 |
| Public development fixtures and grader recomputation | None | Methods | Figure 2 |
| Paired scientific-validity outcomes | Results; final Impact | Results; primary table; Conclusion | Figure 3 |
| Tokens, dated price, wall time, retry events | Results if central | Results and Discussion | Figure 4 |
| Injected recoverable-failure subset | Results if central | Methods, Results, Discussion | Figure 4 |
| Complete failure taxonomy and selected case index | None unless central | Results and Discussion | Figure 5 |
| Limitations and negative/null findings | Honest final Impact | Discussion and Conclusion | Figures 3–5 where applicable |
