# Public/challenge validity plan

This plan tests whether the generated MRI/MRSI failure mechanisms survive contact
with external data. It is not implemented evidence and it does not authorize data
redistribution or clinical claims.

## MRI arm

Candidate source: [NYU fastMRI](https://fastmri.med.nyu.edu/), using only data
obtained under its then-current access agreement. The repository will contain an
adapter, integrity hashes, acquisition filters, and split identifiers—not images,
k-space, headers, or derived patient-level artifacts.

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

## Leakage and release boundary

Private or agreement-controlled data remain outside Git and outside provider
prompts. Model-visible task descriptions contain only approved derived metadata.
Evaluator references remain isolated. Any release includes code, configuration,
checksums, and synthetic fixtures only unless the source license explicitly
permits more.

