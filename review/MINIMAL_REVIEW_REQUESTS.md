# Minimal executable reviewer requests

Review target: the current candidate lock and source revision named in
[`SIGNOFF.md`](SIGNOFF.md). Historical numbered locks are retained for audit and
must not be substituted for that target.

Decision before review: **NO-GO**

Reviewers should use an isolated environment and must not provide patient data,
credentials, private evaluator inputs, or unpublished spectra/images. Commands
write only disposable development outputs.

## Common verification — all reviewers

```bash
python3.12 -m venv .venv-review
.venv-review/bin/pip install -e '.[dev,figures]'
.venv-review/bin/sab-audit-publication --root .
.venv-review/bin/pytest tests/test_publication_audit.py tests/test_protocol_freeze.py
```

Expected audit status is `development-consistent-primary-no-go`; any other status
is a blocking finding. Confirm that the checked-out source and candidate lock
match the identifiers above before completing a form.

## MRI reconstruction reviewer

```bash
PYTHONPATH=src .venv-review/bin/python -m science_agent.mri_recon_pilot \
  --output /tmp/mr-agentguard-mri-review
.venv-review/bin/pytest tests/test_mri_multicoil_research.py \
  tests/test_mri_recon_pilot.py tests/test_public_ingestion.py
```

Return [`MRI_REVIEW_FORM.md`](MRI_REVIEW_FORM.md) with explicit decisions on:

1. forward model, coil-sensitivity, mask, and complex-noise plausibility;
2. zero-fill, SENSE-CG, and oracle roles and parameter-selection rules;
3. magnitude/gradient NRMSE and acquired-data residual thresholds;
4. whether the difficulty strata and boundary cases support the intended claim;
5. whether the OpenNeuro header smoke is correctly limited to ingestion evidence;
6. the minimum raw multi-coil public/challenge validation still required.

## MRS/MRSI reviewer

```bash
PYTHONPATH=src .venv-review/bin/python -m science_agent.mrsi_nuisance_pilot \
  --output /tmp/mr-agentguard-mrsi-review
.venv-review/bin/pytest tests/test_mrsi_nuisance_research.py \
  tests/test_mrsi_nuisance_pilot.py
```

Return [`MRSI_REVIEW_FORM.md`](MRSI_REVIEW_FORM.md) and annotate
[`MRSI_SPECTRAL_AXIS_EVIDENCE.md`](MRSI_SPECTRAL_AXIS_EVIDENCE.md). Resolve
`MRSI-001` explicitly: accept the frequency-domain abstraction for the stated
nuisance-removal claim, or require time-domain acquisition, dwell time, center
frequency, and vendor convention before freeze. Also approve or revise ppm
orientation, drift/phase/lineshape ranges, basis assumptions, nuisance and
metabolite-retention metrics, thresholds, and the minimum external dataset check.

## Statistical reviewer

```bash
PYTHONPATH=src .venv-review/bin/python -m science_agent.design_sensitivity
.venv-review/bin/pytest tests/test_design_sensitivity.py \
  tests/test_primary_manifest.py tests/test_paired_analysis.py
```

Return [`STATISTICAL_REVIEW_FORM.md`](STATISTICAL_REVIEW_FORM.md) with explicit
decisions on the 61 independent instances per family, two repetitions per
condition, 1,220-run matrix, co-primary multiplicity rule, paired estimand,
family-stratified instance-cluster bootstrap, exact sign-flip sensitivity,
missingness, exclusions, and whether the planned interval can support an
informative null result.

## Required response

Each reviewer provides their completed form, conflict declaration, exact source
revision, decision (`Accept`, `Accept with required revisions`, or `Reject`), and
issues with severity and a verifiable resolution condition. Only after all three
required roles accept and every critical/major issue is closed may
[`SIGNOFF.md`](SIGNOFF.md) change the primary decision from NO-GO.
