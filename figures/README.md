# Figure artifacts

This directory will contain versioned plotting code, vector sources, compact immutable analysis inputs, and submission-ready exports for the ISMRM 2027 abstract.

Do not place provisional model outputs, private evaluator fixtures, raw provider responses, or manually edited result graphics here. Until the primary analysis is frozen, result-dependent Figures 3–5 must be visibly labeled as templates and must not contain plausible mock numbers. As of 14 September 2026, every planned figure is `PLANNED`; none is a conference result.

Planned submission files:

- `figure_1_study_design.png`
- `figure_2_task_gallery.png`
- `figure_3_primary_results.png`
- `figure_4_efficiency_recovery.png`
- `figure_5_failure_analysis.png`
- `preview_3x2.png`

Each export will have a JSON sidecar recording its source hashes and rendering environment. See [the complete figure specification](../docs/ISMRM_2027_FIGURES.md).

Paper-level acceptance requires SVG, font-embedded PDF, and high-resolution PNG outputs; a standalone caption; exact denominators and uncertainty where applicable; deterministic success/boundary/failure selection; color-vision, grayscale, final-size, and clipping QA; independent numeric verification; and MR-domain signoff. Portfolio/demo-quality graphics do not pass this gate. Complete [the figure QA record](FIGURE_QA_TEMPLATE.md) separately for every candidate figure.
