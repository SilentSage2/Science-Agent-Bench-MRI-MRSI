# Development figure captions

## Figure 1 — Framework

Implemented evaluation framework for failure-aware MRI/MRSI agents. Versioned
public task inputs enter one of five enforced controller paths. Only allowlisted
MR methods run inside a digest-pinned, network-disabled container; the controller
receives public method diagnostics, while independent physics/fidelity grading
uses evaluator-isolated references. Direct commits before observation, reactive
assesses after one observation, self-debug must revise one successful candidate,
and structured recovery requires a plan and typed replan. This is a design figure;
the primary study remains NO-GO.

## Figure 2 — Task calibration

Generated task calibration for the two depth-target families. Bars show
difficulty-stratified mean error for naive and conventional methods across nine
generated cases per family: magnitude NRMSE for multi-coil MRI and spectral NRMSE
for complex MRSI (lower is better). Conventional methods outperform naive methods
in every calibration case; oracle ceilings and intervals remain in the source
experiment records. The v4 real-model checkout motivated the boundary analysis,
but its single-instance condition counts are excluded. These values demonstrate
task separation, not agent effects, prevalence, clinical performance, or public-
data validity.

