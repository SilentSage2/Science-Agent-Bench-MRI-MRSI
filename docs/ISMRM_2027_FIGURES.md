# ISMRM 2027 figure specification

## Delivery decision

Prepare five review figures and one separate preview image, then submit the strongest four or five after the results freeze. Figures 1–2 can reach design-complete status before the live benchmark. Figures 3–5 must remain labeled as templates until the frozen analysis and selected failure cases exist; synthetic or mock values must never appear as conference results.

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

## Figure 1 — Frozen paired benchmark design

**Purpose:** establish the causal comparison in one glance.

**Panels**

- **A:** the four MRI/MRSI task families with visible inputs and evaluator-isolated references;
- **B:** reactive, plan-only, and plan plus bounded retry/replan state paths;
- **C:** shared model, prompt/tool versions, hard budgets, paired instances, and deterministic grading;
- **D:** primary and secondary outcomes.

**Data dependency:** versioned protocol only. This figure can be completed before live runs and adapted into the preview image.

**Draft caption:** Frozen paired study design. Three controller conditions use identical model, MRI/MRSI instances, tools, prompts, and hard budgets. Policies see only public task state; deterministic evaluators retain hidden references. Primary outcomes are completion, scientific validity, and reproducibility, with efficiency and violations reported separately.

## Figure 2 — MR-specific task and grader gallery

**Purpose:** prove that this is an MR methods study rather than a generic agent demo.

**Panels**

- **A:** MRS basis-model selection: observed spectrum, candidate fits, and residual region;
- **B:** MRSI nuisance removal: contaminated and corrected voxel spectra with water/lipid bands;
- **C:** undersampled MRI reconstruction: mask, zero-filled image, reconstruction, and error map;
- **D:** subject-level split audit: compact subject/session-to-split diagram with detected violations.

**Data dependency:** one frozen public development instance per family. Images and spectra come directly from generator outputs and independent grader recomputation.

**Draft caption:** Four deterministic MR workflow families. Tasks cover MRS model selection, MRSI nuisance suppression, Cartesian MRI reconstruction, and subject-level leakage auditing. Each task produces machine-readable artifacts and MR-specific evidence; graders independently recompute conclusions using evaluator-isolated parameters where required.

## Figure 3 — Primary paired scientific-validity result

**Purpose:** carry the main abstract result.

**Panels**

- **A:** task-instance matrix for scientific validity by controller and repetition;
- **B:** paired effect estimates for plan-only and retry/replan versus reactive, with 95% intervals;
- **C:** family-stratified effects and denominators.

**Data dependency:** frozen 72-run primary comparison plus versioned paired analysis. Intervals and resampling unit must match the analysis plan.

**Draft caption template:** Paired scientific-validity outcomes across four MRI/MRSI task families. The matrix shows every frozen instance and repetition; effect estimates compare each structured controller with reactive execution using task-instance pairing. Points denote [ESTIMAND] and intervals denote [METHOD]. Values are inserted only by the frozen analysis command.

## Figure 4 — Efficiency and failure recovery

**Purpose:** determine whether any validity gain is worth its budget cost.

**Panels**

- **A:** scientific validity versus median provider-reported token use;
- **B:** cost and wall time per valid completion with intervals;
- **C:** outcomes after injected recoverable failures, separated into recovered, repeated, stopped, and invalid completion.

**Data dependency:** complete provider usage, dated pricing snapshot, wall-clock records, and the preregistered injected-failure subset. If provider usage is incomplete, omit cost-normalized claims rather than imputing zero.

**Draft caption template:** Efficiency and recovery under identical hard budgets. Controller-level validity is shown against tokens, dated estimated cost, and wall time; the injected-failure subset separates successful recovery from repetition, termination, and invalid completion. Error bars show [METHOD]. Missing provider usage is reported and excluded from normalized estimates.

## Figure 5 — MR failure analysis

**Purpose:** translate aggregate agent errors into recognizable MR scientific failure modes.

**Panels**

- **A:** reconstruction case with acquired-sample consistency violation and spatial error map;
- **B:** MRSI correction case with metabolite attenuation despite strong nuisance suppression;
- **C:** MRS model-selection case with plausible fit but unsupported conclusion;
- **D:** leakage-audit case with missed subject/session overlap;
- **E:** compact taxonomy with counts by controller.

**Data dependency:** failure cases selected by a frozen rule, not by visual appeal. Each displayed artifact must link to its run ID, hash, grader report, and corresponding matched comparison.

**Draft caption template:** Representative MRI/MRSI scientific failures selected by a prespecified severity-and-frequency rule. Examples show data-consistency violation, metabolite loss, unsupported model selection, and missed split leakage. The taxonomy summarizes all primary runs; displayed cases retain run identifiers and artifact hashes for exact reproduction.

## Preview figure

Use a simplified 3:2 derivative of Figure 1 with three large controller paths entering the same MRI/MRSI task block and one outcome statement. It must contain no small axes, captions, institution logos, model branding, or unblinded headline number until the analysis is frozen. Export under 1 MB as a high-quality PNG if the 2027 system retains the prior specification.

## Reproducible data interfaces

Final rendering commands will consume only immutable inputs:

- `analysis/paired_outcomes.json`: one row per condition, instance, and repetition;
- `analysis/effect_estimates.json`: estimands, confidence intervals, denominators, and methods;
- `analysis/efficiency.json`: tokens, priced cost, wall time, retries, and missingness flags;
- `analysis/failure_index.json`: prespecified selected run IDs, categories, and artifact hashes;
- frozen task input/output directories for the four Figure 2 examples.

Every rendered figure must include a sidecar manifest with the Git commit, source-data hashes, plotting-command version, dimensions, and output hash. Manual changes after scripted export are prohibited unless represented in a versioned vector source and reproduced by the build command.

## Production and QA gates

| Date | Gate |
|---|---|
| 20 Sep | Figure 1 wireframe, palette, typography, and panel grid frozen |
| 27 Sep | Figure 2 generated from frozen development fixtures |
| 30 Sep | Empty Figure 3–5 templates pass data-schema tests |
| 10 Oct | Primary data frozen; no visual tuning based on desired conclusions |
| 14 Oct | First complete Figure 3–5 render and captions |
| 18 Oct | MR-domain scientific review and statistical review complete |
| 22 Oct | Phone-size, grayscale, PDF/SVG/PNG, and caption-length QA complete |
| 25 Oct | Upload all figures to ECHO and inspect its rendered abstract preview |

Final QA requires: correct ppm orientation, consistent image windowing, visible scale/color bars, readable phone-size preview, no clipped labels, no unexplained abbreviations, exact denominators, captions under the current limit, source/result hash agreement, and independent verification of every plotted number.

