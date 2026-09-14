# Figure QA record template

Copy this file once per candidate figure and commit the completed record beside its outputs. A checked box is a reviewer assertion, not an automated claim. Any unresolved item keeps the figure in `PLANNED` or `DESIGN` status.

## Identity

- Figure:
- Status: `PLANNED` / `DESIGN` / `RESULT`
- Contract version or Git commit:
- Rendering command and commit:
- Source-data/config hashes:
- Output SVG/PDF/PNG hashes:
- Task/run IDs and inclusion/exclusion counts:

## Scientific evidence

- [ ] The permitted claim and observation that would weaken/refute it are unchanged from the preregistered contract.
- [ ] The baseline, controlled ablations, analysis unit, metric direction, and validity threshold are explicit.
- [ ] The full eligible sample is represented; missing data, exclusions, and reruns follow frozen rules.
- [ ] Sample size and all panel denominators are shown.
- [ ] Error bars/intervals name their estimand, level, method, resampling unit, repetition count, and seed.
- [ ] Raw paired points or the complete task-instance matrix are shown where the contract requires them.
- [ ] Secondary, sensitivity, exploratory, and injected-failure results are labeled and separated from the primary endpoint.
- [ ] Null, adverse, boundary, and failed outcomes have not been hidden.
- [ ] Qualitative cases follow the deterministic success/boundary/failure selection rule; ties and absent categories are recorded.
- [ ] Each qualitative artifact resolves to its task ID, run ID, controller, grader report, threshold, and hash.
- [ ] Diagrammed components and data paths match the released implementation.
- [ ] The caption is standalone and makes no claim beyond the plotted evidence.

## Numeric and MR-domain review

- [ ] A clean-environment rerun reproduces all plotted values and output hashes from the locked inputs/config.
- [ ] An independent reviewer traced every displayed number to the analysis output.
- [ ] A statistical reviewer approved pairing, uncertainty, missingness, and multiplicity language.
- [ ] An MR-domain reviewer approved k-space conventions, image orientation/windowing, ppm direction, units, spectral annotations, and scientific interpretation as applicable.

## Visual and export review

- [ ] SVG and font-embedded PDF masters plus a high-resolution PNG exist.
- [ ] Rasterized SVG, PDF, and PNG were inspected at final submission size.
- [ ] Panel labels are 11–12 pt equivalent and remaining text is at least 8.5 pt equivalent.
- [ ] Axes include units; legends, scale bars, color bars, and uncertainty definitions are complete.
- [ ] Compared images/maps use prespecified, shared windows or color limits.
- [ ] Meaning survives color-vision simulation and grayscale conversion without relying on color alone.
- [ ] No label, marker, line, or error bar is clipped, obscured, or illegible.
- [ ] Caption character count and file dimensions/size satisfy the current official submission rules.
- [ ] No untracked manual edit was made after scripted export.

## Signoff

- Numeric reviewer / date:
- Statistical reviewer / date:
- MR-domain reviewer / date:
- Visual QA reviewer / date:
- Final disposition and unresolved limitations:
