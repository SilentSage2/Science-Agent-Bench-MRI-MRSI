# Reviewer bundle index

Status: **NO-GO / unsigned**  
Publication-facing name: **MR-AgentGuard**

Send reviewers a link to one immutable Git revision and this file. Reviewers
must record decisions in their role-specific form; email approval without a
revision and completed form is not sufficient.

## Common core — 15 to 30 minutes

1. Read [`README.md`](README.md), [`PROTOCOL_V1.md`](PROTOCOL_V1.md), and
   [`ISSUE_LOG.md`](ISSUE_LOG.md).
2. Confirm the controller condition is the intervention, the two MR families are
   analyzed separately, and hidden scores never enter the policy.
3. Confirm development pilots and Figures 1–2 are mechanism/calibration evidence,
   not agent-effect estimates.
4. Record every critical or major concern in the issue log.

## MRI reconstruction reviewer — 60 to 90 minutes detailed

Read [`MRI_REVIEW_FORM.md`](MRI_REVIEW_FORM.md), the multi-coil pilot and silent-
invalidity records listed in [`REVIEW_PACKET_MANIFEST.json`](REVIEW_PACKET_MANIFEST.json),
and [`../docs/OPENNEURO_DS004068_INGESTION.md`](../docs/OPENNEURO_DS004068_INGESTION.md).

Check coil-sensitivity and noise assumptions, sampling masks, zero-fill/SENSE-CG/
oracle roles, magnitude and gradient endpoints, thresholds, boundary cases, and
whether 61 independent groups per family cover the intended claim. Treat the
OpenNeuro smoke only as metadata/license/checksum/split evidence: it contains no
raw multi-coil k-space and cannot validate reconstruction physics.

## MRS/MRSI reviewer — 60 to 90 minutes detailed

Read [`MRSI_REVIEW_FORM.md`](MRSI_REVIEW_FORM.md) and
[`MRSI_SPECTRAL_AXIS_EVIDENCE.md`](MRSI_SPECTRAL_AXIS_EVIDENCE.md). Check ppm
orientation, spectrometer-frequency conversion, frequency/phase drift,
mixed-lineshape and basis assumptions, metabolite retention, nuisance endpoints,
thresholds, and boundary cases. Decide explicitly whether the frequency-domain
abstraction is acceptable or whether MRSI-001 requires a time-domain acquisition,
dwell-time, center-frequency, and vendor-convention extension.

## Statistical reviewer — 60 to 90 minutes detailed

Read [`STATISTICAL_REVIEW_FORM.md`](STATISTICAL_REVIEW_FORM.md),
`../protocol/blinded_primary_design_v1.json`, and the primary-manifest and paired-
analysis source listed in the packet manifest. Check the 61-group/family
sensitivity assumptions, two repetitions per condition, paired estimand,
family-stratified reporting, co-primary multiplicity rule, instance-cluster
bootstrap, exact sign-flip sensitivity, exclusions, and missingness handling.

## Agent/evaluation reviewer — recommended

Read [`AGENT_CONTROL_REVIEW_FORM.md`](AGENT_CONTROL_REVIEW_FORM.md) and the
controller adversarial fixture. Verify that direct precommits before observation,
reactive assesses after observation, self-debug must revise a successful
candidate, and plan/recovery paths have distinct enforced trajectories.

## Acceptance gate

Each required reviewer must choose `Accept` or `Accept with required revisions`,
all required revisions must be verified, no critical or unresolved major issue
may remain, and [`SIGNOFF.md`](SIGNOFF.md) must identify the exact revision and
executor digest. Until then the primary run is not authorized.
