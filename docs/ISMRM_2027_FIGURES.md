# ISMRM 2027 figure specification

## Delivery decision

Prepare five review figures and one separate preview image for this MRI/MRSI agent-benchmark project, then submit the strongest four or five after the results freeze. This is one of two intended ISMRM target projects; its data, claims, manifests, and QA records remain project-specific unless a prospectively frozen joint protocol says otherwise. Figure 1 is a methods/framework overview and Figure 2 is a generated-task gallery, so both can reach design-complete status before the live benchmark. Figures 3–5 are empirical result figures and must remain labeled as templates until the frozen analysis and selected cases exist; synthetic or mock values must never appear as conference results.

**Current status (14 September 2026): reproducible development Figure 1 and Figure 2 exports exist and passed visual/export QA, but independent MR-domain signoff is pending. Figures 3–5 and the preview remain `PLANNED`; no submission-ready empirical result figure exists.** Development calibration is not a controller result. A status can change to `RESULT` only when the frozen-data command, sidecar manifest, independent number check, and visual/scientific QA records all pass.

The detailed 2027 instructions must be rechecked when submissions open. The current production targets follow the prior official guidance: no more than five review figures, captions no longer than 500 characters, and a separate simple preview figure that remains legible on a phone. The prior submission system additionally required a 3:2 preview image under 1 MB.

- [Prior standard abstract figure limits](https://www.ismrm.org/26m/call/standard/)
- [Prior ECHO upload guidance](https://www.ismrm.org/26m/call/submission-guide/)

## Visual system

- Canvas: white background; no decorative gradients, shadows, or three-dimensional chart effects.
- Type: one sans-serif family; panel labels 11–12 pt equivalent, axes at least 8.5 pt at final size.
- Palette: color-vision-safe blue `#0072B2`, orange `#E69F00`, green `#009E73`, vermilion `#D55E00`, and neutral grays. Controller identity must also be encoded by marker or line style.
- Images: grayscale MR magnitude images with a shared window; perceptually uniform maps for residuals; never use rainbow/jet.
- Spectra: consistent ppm direction and limits, explicit metabolite/water/lipid annotations, and line styles that remain separable in grayscale.
- Statistics: show denominators, raw paired points where space permits, effect estimates, and interval definitions. Do not use bar charts without uncertainty.
- Export: retain SVG/PDF masters; generate high-resolution PNG submission copies; embed fonts; crop whitespace consistently.
- Accessibility: every scientific distinction survives grayscale conversion; captions define abbreviations and uncertainty.

## Paper-level evidence contract

Every figure must have a versioned contract before rendering. The contract names the scientific statement the figure may support, the observation that would weaken or refute it, the comparison and analysis unit, the frozen source data, the prespecified sample-selection rule, statistical treatment, required panels, and prohibited interpretations. A figure is rejected if any contract field is unresolved.

Global rules:

1. A framework or methods overview need not contain experimental statistics. It must be structurally accurate, independently captioned, and visually publication-ready. Every node and arrow maps to a released component or is explicitly labeled `PLANNED`; decorative or aspirational data flow is prohibited.
2. Empirical plots use the frozen protocol and complete eligible run set. Filtering after viewing outcomes is prohibited; exclusions and missingness appear in the figure manifest.
3. Reactive execution is the meaningful primary baseline. Plan-only is the planning ablation; plan plus retry/replan isolates the additional recovery mechanism. No controller claim may be made from an unpaired comparison.
4. Primary uncertainty uses independent task instance as the paired resampling unit; repeated model calls remain nested within instance-condition cells. Set `n` and repetition count by a blinded design-stage sensitivity analysis rather than deadline convenience, then report scheduled, completed, and excluded counts. Use a seeded, versioned task-family-stratified cluster bootstrap across instances for 95% intervals; label small-sample inference as exploratory. Report the paired point estimate even when its interval includes zero.
5. Secondary metrics and injected-failure analyses are labeled secondary. Multiplicity is disclosed; isolated nominal significance is not promoted as a primary claim. A paired exact sign-flip/randomization sensitivity analysis is reported when its assumptions match the frozen estimand. Exact test choices and seeds must be frozen before the results are opened.
6. Qualitative selection is deterministic. A displayed case never substitutes for the all-run distribution and always carries task ID, run ID, controller, grader score, threshold, and artifact hash.
7. Captions stand alone: population, `n`, comparison, metric direction, interval method, selection rule, abbreviations, and limitation are stated when applicable without overstating causality or generalization.
8. Every final figure exports an editable SVG and font-embedded PDF plus a high-resolution PNG. At final column/page scale, axes and legends are at least 8.5 pt, panel labels 11–12 pt, physical units are explicit, and all encodings pass color-vision and grayscale checks.
9. All plotted values are generated by a versioned command from hash-locked data and configuration. Manual numeric entry, untracked Illustrator edits, and cherry-picked reruns are prohibited. A second reviewer verifies every number and a domain reviewer signs off on MR interpretation.

## Figure 1 — Frozen paired benchmark design

**Status:** `DESIGN-COMPLETE / MR-SIGNOFF-PENDING`, never an empirical result figure.

**Permitted scientific statement:** the implemented system accepts versioned MRI/MRSI task inputs, uses a provider-neutral single-agent controller to select allowlisted actions under hard budgets, feeds typed observations back into the condition path, and produces hashed artifacts, trajectories, and independent grades. Multi-coil MRI and complex-MRSI research bindings traverse the tested isolated execution boundary; fixed-path development bindings remain trusted host-side smoke infrastructure. A future paired study must hold model, tasks, tools, budgets, and evaluators constant and eliminate the direct/reactive and successful-candidate self-debug ambiguities exposed by the development pilot.

**Would weaken/refute the statement:** any condition-specific prompt, tool, budget, task exposure, hidden-reference access, or non-paired instance assignment. Such a discrepancy blocks the figure and the primary comparison.

**Analysis unit and selection:** every frozen included family and all primary/baseline conditions; no sample selection. Solid styling denotes implemented components. Dashed styling is reserved for explicitly labeled planned research-grade tool bindings and may not be visually conflated with released components.

**Statistics:** not applicable. This figure describes the frozen design and must not imply an observed effect.

**Panels**

- **A — inputs:** versioned task specification, public MRI/MRSI inputs, controller condition, prompt/tool versions, and hard budget; evaluator-isolated references enter only the grader path;
- **B — core components:** provider-neutral model adapter, reactive/plan-only/retry-replan controller, state machine, budget ledger, immutable tool registry, and trajectory writer;
- **C — execution and feedback:** typed action → allowlist/budget reservation → trusted development binding or digest-pinned Docker research binding → typed observation/artifact hashes → controller feedback, including the single bounded retry/replan branch;
- **D — outputs and evaluation:** run manifest, append-only trajectory, scientific artifacts, deterministic grader, and separated validity, reproducibility, efficiency, and policy-violation outcomes.

**Data dependency:** versioned protocol only. This figure can be completed before live runs and adapted into the preview image.

**Development caption:** MR-AgentGuard framework and paired design. Versioned public inputs and a hard budget enter one of five enforced controller paths; allowlisted Docker-bound actions return typed observations and hashed artifacts for independent grading, while hidden references never enter the policy path. The primary study remains NO-GO pending review and freeze.

## Figure 2 — Core MR task calibration

**Status:** `DEVELOPMENT-CALIBRATION / MR-SIGNOFF-PENDING`, not evidence of controller performance.

**Permitted scientific statement:** across nine generated cases per core family, the conventional MRI/MRSI method has lower mean task error than the naive method in each difficulty stratum. This establishes task separation only.

**Would weaken/refute the statement:** a panel whose conclusion can be graded without MR-specific quantities, a displayed value not independently recomputed, evaluator-reference leakage, or inconsistent physical units/orientation.

**Analysis unit and selection:** all nine frozen generated calibration cases in each of the MRI and MRSI core families, summarized by predeclared difficulty. The immutable source JSON records the values and hashes.

**Statistics:** difficulty-stratified descriptive mean NRMSE only. The source records paired calibration intervals, but the development figure does not present them as inference. No agent effect, prevalence, public-data validity, or clinical generalization is permitted.

**Panels**

- **A:** MRI magnitude NRMSE for naive zero-fill and conventional SENSE-CG by difficulty;
- **B:** MRSI spectral NRMSE for fixed-template and adaptive nuisance removal by difficulty.

**Data dependency:** `experiments/baseline_figure_data_v1.json`, with `research_result=false`; v4 condition counts are explicitly excluded.

**Development caption:** Generated task calibration for multi-coil MRI and complex MRSI. Bars show difficulty-stratified mean naive and conventional NRMSE across nine cases per family (lower is better). Values demonstrate task separation, not agent effects, prevalence, public-data validity, or clinical performance.

## Figure 3 — Silent-invalidity prevention and recognition

**Status:** `PLANNED — EMPTY TEMPLATE`; it must contain no plausible placeholder values.

**Primary MR claim under test:** controller strategy changes how often technically completed MRI/MRSI outputs pass hidden physics/fidelity checks and how often an invalid output is explicitly recognized rather than endorsed.

**Support/refutation rule:** support requires a positive paired effect with its 95% interval and task-family consistency shown. An interval spanning zero is reported as inconclusive; a negative estimate supports harm. No wording of “improves” is allowed solely from a higher aggregate pass count.

**Baseline and ablations:** reactive is the primary controller baseline; plan-only isolates initial planning; plan plus retry/replan versus plan-only isolates bounded recovery. Direct generation and budget-matched self-debug are competitive agent baselines. Conventional, naive, and oracle MR methods calibrate task difficulty and validity but are not pooled with agent effects.

**Sample and statistics:** the implemented blinded sensitivity design specifies 61 independent instances per family and two repetitions per condition (1,220 scheduled runs), pending statistical and domain signoff. The primary estimand is the paired difference in mean scientific-validity completion, averaging repetitions within each instance-condition cell. Show the seeded task-family-stratified cluster-bootstrap 95% interval, raw paired outcomes, denominators, incomplete runs, and prespecified exclusions.

**Panels**

- **A:** task-instance matrix separating technical completion, hidden MR validity, and final agent recognition by condition and repetition;
- **B:** paired effects for invalidity prevention and detection versus reactive, direct, and self-debug baselines, with 95% intervals;
- **C:** MRI/MRSI family-stratified effects, continuous fidelity metrics, and exact denominators.

**Data dependency:** sensitivity-justified frozen primary comparison plus versioned paired analysis. Intervals and resampling unit must match the analysis plan.

**Draft caption template:** Paired silent-invalidity outcomes across frozen MRI/MRSI tasks. The matrix separates error-free technical completion from hidden physics/fidelity validity and agent recognition. Effects compare controller strategies with reactive, direct, and self-debug baselines using task-instance pairing. Points denote [ESTIMAND]; intervals denote [METHOD]. Values come only from the frozen analysis.

## Figure 4 — Efficiency and failure recovery

**Status:** `PLANNED — EMPTY TEMPLATE`; it must contain no plausible placeholder values.

**Secondary claims under test:** any reduction in silently endorsed MR-invalid outputs is accompanied by a measurable token, cost, and wall-time tradeoff; the retry/replan mechanism changes recovery specifically after prespecified acquisition/processing failures.

**Would weaken/refute the claims:** overlapping paired uncertainty, worse cost per valid completion, incomplete provider usage, or no improvement over plan-only in the injected-failure subset. Null and adverse results remain in the figure.

**Baseline, ablations, and statistics:** use the same sensitivity-justified paired instances and nested repetitions as Figure 3. Contrast structured controllers with reactive, direct, and self-debug for efficiency and retry/replan with plan-only for recovery. Show raw paired instance points where legible and the same seeded cluster-bootstrap interval definition. Analyze injected failures separately from the primary endpoint and report their exact `n`; never pool them into the primary success estimate.

**Panels**

- **A:** prevented or recognized silent invalidity versus provider-reported token use;
- **B:** cost and wall time per hidden-valid or correctly flagged completion with intervals;
- **C:** outcomes after injected recoverable failures, separated into recovered, repeated, stopped, and invalid completion.

**Data dependency:** complete provider usage, dated pricing snapshot, wall-clock records, and the preregistered injected-failure subset. If provider usage is incomplete, omit cost-normalized claims rather than imputing zero.

**Draft caption template:** Efficiency and recovery under identical hard budgets. Controller-level validity is shown against tokens, dated estimated cost, and wall time; the injected-failure subset separates successful recovery from repetition, termination, and invalid completion. Error bars show [METHOD]. Missing provider usage is reported and excluded from normalized estimates.

## Figure 5 — MR failure analysis

**Status:** `PLANNED — EMPTY TEMPLATE`; no case may be selected before the run freeze.

**Scientific statement under test:** aggregate validity failures correspond to identifiable MR failure modes rather than only formatting or infrastructure errors.

**Would weaken/refute the statement:** most invalid runs lack an MR-specific failure, categories cannot be reproduced by a blinded second reviewer, or conclusions depend on visually selected examples. Report these outcomes rather than replacing cases.

**Selection contract:** classify every eligible primary run using the frozen taxonomy before viewing controller totals. For each displayed MR modality, show a deterministic success/boundary/failure triptych when available: the valid run nearest the within-category median score, the run closest to the preregistered validity threshold, and the most severe invalid run. Break ties by lexicographic run ID. If a category is absent, show an explicit “no eligible case” panel. Include the all-run category counts and blinded-review agreement so examples cannot stand in for prevalence.

**Panels**

- **A:** MRI reconstruction success/boundary/failure cases with acquired-sample consistency and shared-scale spatial error maps;
- **B:** MRSI correction success/boundary/failure spectra showing nuisance suppression and metabolite retention;
- **C:** MRS model-selection success/boundary/failure fits and residual evidence;
- **D:** leakage-audit success/boundary/failure diagrams with missed or correctly identified overlap;
- **E:** compact taxonomy with counts by controller.

**Data dependency:** complete frozen run index, grader reports, blinded failure labels, and deterministic selection output. Each displayed artifact must link to its task ID, run ID, controller, score and threshold, hash, grader report, and matched comparison.

**Draft caption template:** Prespecified MRI/MRSI success, boundary, and failure cases from the frozen primary runs. Deterministic score-based selection prevents visual cherry-picking; absent categories remain explicit. The taxonomy summarizes all eligible runs by controller, and each case reports its task/run identifier, validity threshold, and artifact hash. [AGREEMENT METHOD] quantifies blinded taxonomy reproducibility.

## Preview figure

**Status:** `PLANNED — DESIGN/PROTOCOL`. Use a simplified 3:2 derivative of Figure 1 with three large controller paths entering the same MRI/MRSI task block and one outcome statement. It must contain no small axes, captions, institution logos, model branding, or unblinded headline number until the analysis is frozen. Export under 1 MB as a high-quality PNG if the 2027 system retains the prior specification.

## Reproducible data interfaces

Final rendering commands will consume only immutable inputs:

- `analysis/paired_outcomes.json`: one row per condition, instance, and repetition;
- `analysis/effect_estimates.json`: estimands, confidence intervals, denominators, and methods;
- `analysis/efficiency.json`: tokens, priced cost, wall time, retries, and missingness flags;
- `analysis/failure_index.json`: prespecified selected run IDs, categories, and artifact hashes;
- frozen task input/output directories for the four Figure 2 examples.

Every rendered figure must include a sidecar manifest with the Git commit, source-data hashes, plotting-command version, dimensions, and output hash. Manual changes after scripted export are prohibited unless represented in a versioned vector source and reproduced by the build command.

The sidecar must additionally record figure status (`PLANNED`, `DESIGN`, or `RESULT`), contract version, exact sample IDs, inclusion/exclusion counts, metric and interval definitions, resampling seed, software lock hash, output DPI, embedded-font check, grayscale/color-vision checks, caption character count, number-review signoff, MR-domain signoff, and visual-QA signoff. A `RESULT` status with any missing field fails the build.

## Production and QA gates

| Date | Gate |
|---|---|
| 20 Sep | Figure 1 wireframe, palette, typography, and panel grid frozen |
| 27 Sep | Figure 2 generated from frozen development fixtures |
| 30 Sep | Empty Figure 3–5 templates pass data-schema tests |
| 10 Oct | Sensitivity-justified primary data frozen; no visual tuning based on desired conclusions |
| 14 Oct | First complete Figure 3–5 render and captions |
| 18 Oct | MR-domain scientific review and statistical review complete |
| 22 Oct | Phone-size, grayscale, PDF/SVG/PNG, and caption-length QA complete |
| 25 Oct | Upload all figures to ECHO and inspect its rendered abstract preview |

Final QA requires: correct ppm orientation, physical units, consistent image windowing, identical color limits for compared maps, visible scale/color bars, readable final-size and phone-size renders, no clipped labels, no unexplained abbreviations, exact denominators and missingness, captions under the current limit, source/result hash agreement, color-vision and grayscale survival, embedded fonts in vector exports, and independent verification of every plotted number. The QA reviewer must inspect rasterized SVG/PDF/PNG outputs rather than only the plotting source.
