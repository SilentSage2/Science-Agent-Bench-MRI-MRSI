# Public/challenge validity plan

This plan tests whether the generated MRI/MRSI failure mechanisms survive contact
with external data. A real OpenNeuro header-only ingestion smoke is implemented,
but no external reconstruction or spectroscopy physics validation exists. The
metadata smoke does not authorize data redistribution or clinical claims.

## MRI arm

Implemented metadata source: OpenNeuro `ds004068` snapshot `1.0.3`. Two
allowlisted BIDS T2w JSON projections and CC0 evidence validate snapshot hashes,
field/acquisition mapping, sensitive-field exclusion, and subject-level split
enforcement. The source contains image-domain metadata rather than raw multi-coil
k-space, so it cannot validate coil sensitivities, reconstruction endpoints, or
the synthetic failure mechanism.

Physics-validation candidate: [NYU fastMRI](https://fastmri.med.nyu.edu/), using only data
obtained under its then-current access agreement. The repository will contain an
adapter, integrity hashes, acquisition filters, and split identifiers—not images,
k-space, headers, or derived patient-level artifacts.

The terms check on 14 September 2026 found that access requires an individual
application and agreement, use is limited to internal research/education, and
redistribution requires prior permission. The code repository's MIT license does
not replace the dataset agreement.

The validation target is mechanism-level: whether zero-filled and conventional
parallel-imaging reconstructions remain separated by acquired-sample consistency,
image fidelity, and edge/gradient fidelity across prospectively chosen knee or
brain multi-coil cases. Subject/exam identifiers define the split unit. Slices
from one exam must never cross development and validation. Coil-map estimation,
normalization, acceleration masks, crop/resolution handling, and reference-image
construction require MRI expert approval before any scoring threshold is set.

## MRS/MRSI arm

Candidate sources are the [ISMRM MRS Fitting
Challenge](https://www.ismrm.org/workshops/Spectroscopy16/mrs_fitting_challenge/)
for spectral-method sanity checks and datasets indexed by
[MRSHub](https://mrshub.org/datasets_mrsi/) only after dataset-specific license,
consent, redistribution, and metadata review. A fitting challenge is not silently
relabeled as spatial MRSI validation.

The first external check maps the encoded ppm axis, field strength, spectral
width, dwell/header convention, phase/frequency offset, linewidth, baseline, and
metabolite/nuisance definitions to the selected source. If raw or reference
nuisance components are unavailable, evaluation is limited to observable
surrogates and blinded expert ratings; hidden synthetic component error remains a
simulation-only endpoint. Subject and acquisition—not voxels or augmented
spectra—define independence.

The challenge page describes 28 synthetic datasets at 123.2 MHz using PRESS,
TE=30 ms, 4,000 Hz spectral width, and 2,048 points, with water-suppressed and
water FIDs plus basis/macromolecular files. Those properties differ materially
from the current 256-point, 0.5–5.0 ppm nuisance simulator. The initial adapter is
therefore a spectral-axis/basis sanity check, not spatial MRSI validation. The
page does not state a clear redistribution license; reuse terms remain a blocking
field rather than being inferred from public download links.

## Prospective acceptance criteria

Before data access, reviewers must approve:

1. source version, license/access record, intended-use statement, and integrity
   procedure;
2. inclusion/exclusion rules and subject/exam/acquisition split keys;
3. mapping from external metadata to the generated parameter ranges;
4. conventional baseline implementation and parameter-selection rule;
5. external endpoints, threshold source, uncertainty method, and handling of
   missing reference data;
6. a minimum case count selected independently of observed controller outcomes;
7. which claims may generalize and which remain simulation-only.

External validation is **NO-GO** until those fields are frozen. It may refute the
simulator; such a negative result is retained rather than tuned away.

The synthetic registry smoke remains executable without downloading either
candidate physics dataset:

```bash
PYTHONPATH=src python3.12 -m science_agent.public_ingestion \
  --registry protocol/public_sources_v1.json \
  --manifest protocol/public_ingestion_smoke_manifest_v1.json \
  --data-root tests/fixtures/public_ingestion \
  --smoke-mode
```

This checks the source registry, required MRI/MRSI mapping fields, file hashes,
path containment, unique acquisitions, and subject/exam/acquisition split
leakage. It intentionally fails if used as real ingestion without an explicit
access/license approval record.

The real OpenNeuro projected-header smoke is separately documented in
[`OPENNEURO_DS004068_INGESTION.md`](OPENNEURO_DS004068_INGESTION.md). Passing it
is ingestion evidence only, never MRI reconstruction-validity evidence.

## Leakage and release boundary

Private or agreement-controlled data remain outside Git and outside provider
prompts. Model-visible task descriptions contain only approved derived metadata.
Evaluator references remain isolated. Any release includes code, configuration,
checksums, and synthetic fixtures only unless the source license explicitly
permits more.
