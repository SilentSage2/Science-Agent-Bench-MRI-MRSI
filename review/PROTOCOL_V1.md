# Protocol synopsis for expert review (version 1)

## Question and scope

The study asks whether agent control strategies, under matched model, tools and
hard budgets, prevent or recognize technically successful but scientifically
invalid MRI reconstruction and MRSI nuisance-removal results. The work concerns
computational research workflows on generated or properly licensed public data;
it makes no diagnostic, treatment, or clinical-deployment claim.

The two co-primary endpoints are (1) prevention of hidden scientific invalidity
among technically completed runs and (2) recognition of invalidity among
technically completed invalid runs. Execution success, artifact presence, and
schema validity are secondary process measures and never substitute for MR
validity.

## Tasks and hidden evaluation

The MRI task uses noisy undersampled multi-coil Cartesian data, complex coil
sensitivities, variable-density masks, and explicit data-consistency checks. Zero
fill is the naive baseline; regularized SENSE-CG is the conventional baseline;
fully sampled reference access is an evaluator-only sanity ceiling. Hidden
grading separates magnitude fidelity, gradient fidelity, and sampled-data
residual so a visually plausible or data-consistent result can still fail.

The MRSI task uses a spatial grid of complex spectra with metabolite-like NAA,
Cr, Cho, and Glx components, frequency and zero/first-order phase drift,
Gaussian/Lorentzian lineshape mismatch, spatial amplitude variation, complex
baseline, and noise. Fixed-template projection is the naive baseline; adaptive
shift, width, and mixed-lineshape modeling is the conventional baseline; hidden
component knowledge is an evaluator-only ceiling. Hidden grading separates
nuisance removal, metabolite retention, and spectral fidelity.

Reviewers must determine whether the parameter ranges are literature- or
data-justified, whether baselines are credible implementations, whether hidden
metrics reflect relevant failure modes, and whether thresholds remain meaningful
near realistic boundary cases. Development seeds, repetitions, and voxels are
not independent biological samples.

## Conditions and fairness

The intended comparison contains direct, self-debug, reactive, plan-only, and
plan plus bounded retry/replan conditions. They share one pinned model snapshot,
task instance, public prompt content, allowlisted tools, token limits, tool-call
limits, wall-time limits, artifact limits, and provider settings. Hidden data and
scores are never visible to a controller.

The v4 development implementation was not freeze-ready because direct and
reactive followed the same mechanics and self-debug only reacted to typed
execution failure. Protocol v1.1 makes direct precommit its validity assessment
before its sole tool call and receive no post-observation model turn; reactive
assesses after its first successful observation. Self-debug must use public
diagnostics to make exactly one revised successful candidate, and the runtime
rejects an early final. These mechanics have trajectory-level development tests
but still require external verification before signoff. Direct is a prevention
baseline and is excluded from the post-observation recognition contrast.
Any condition-specific instruction or action opportunity must be documented as
part of the intervention rather than silently added after observing outcomes.

## Design and analysis

The proposed blinded design uses 61 independent latent instances per family,
derived for a 20 percentage-point paired difference, 0.35 discordance, two-sided
alpha 0.05, and 80% power. It assigns 20/21/20 instances to easy/moderate/hard and
two model repetitions per instance-condition. This is a review target, not a
frozen or authorized run matrix. The analysis unit is an independent task instance. Model repetitions are paired
within instance and clustered in inference. A blinded design-stage sensitivity
analysis must choose the number of independent MRI and MRSI instances and model
repetitions using plausible event rates/effect sizes, anticipated missingness,
precision targets, and the available cost ceiling. The current 18-instance
development manifest has only six dependence groups and cannot be relabeled as
the confirmatory sample.

The statistical reviewer must freeze the primary estimands, denominators,
pairing, interval method, family/stratum summaries, treatment of provider and
infrastructure failures, retry rules, and multiplicity policy. All randomized or
bootstrap procedures require recorded seeds. Results must include complete
denominators, uncertainty, model/tool usage, wall time, cost, policy violations,
and a prospectively defined failure taxonomy. No condition claim may be based on
one instance per family or unpaired aggregate pass counts.

## Evidence boundaries and stopping

Naive/conventional/oracle calibration demonstrates task separation, not an agent
effect. Scripted runs demonstrate orchestration, not model performance. The paid
two-instance v4 checkout demonstrates feasibility and exposed four silently
invalid MRI endorsements, but the method choices and current control semantics
confound condition effects; its counts are excluded from abstract results.

Primary runs stop for aggregate cost breach, credential or privacy exposure,
grader/data leakage, executor-image mismatch, systematic provider failure, or a
predeclared safety/validity trigger. Corrections after freeze require a versioned
deviation record; affected runs are not silently replaced. A null or negative
result is publishable if the protocol is valid. A harness-only result is not.

## Freeze and release

Signoff binds one Git revision, task-manifest hash, grader hash, prompt/schema
hash, analysis hash, model identifier, provider settings, budget, pricing basis,
and Docker image digest. Private evaluator material remains isolated. Compact
aggregate records may be committed; provider payloads, credentials, generated
runs, private clinical data, and evaluator secrets may not be committed.

After the run, the same reviewers inspect representative successes, boundary
cases, failures, all four/five conference figures, numerical cross-checks, and
claim wording. Post-result review cannot retroactively cure a defective or
unfrozen protocol.
