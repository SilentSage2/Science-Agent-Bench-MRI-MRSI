# MRSI silent-invalidity endpoint validation v1

Status: **endpoint/mechanism validation, not a real-model comparison**
Date: 2026-09-14

## MRSI question

Can a nuisance-removal tool return normally with schema-valid reproducible complex spectra while residual water/lipid contamination and metabolite distortion make the output scientifically invalid?

## Frozen case

- task: `SAB-MRSI-NUIS-CX-001`;
- 4×4 voxels, 256 complex spectral points, hard drift/mismatch stratum;
- generator seed 2301, retained only for this endpoint fixture;
- submitted method: fixed nominal-template projection;
- research image: `sha256:fbb0cde9a40ec156133c67b434a719615f8b2bc3df7744e1087911a0bb950f1c`;
- hidden comparator: adaptive shift/width/mixed-lineshape conventional baseline;
- hidden oracle: exact generated nuisance and baseline components.

## Result

The fixed-projection tool produced valid, numerically self-consistent, reproducible artifacts but hidden grading rejected scientific validity.

| Metric | Fixed projection | Adaptive conventional | Hidden oracle |
|---|---:|---:|---:|
| Nuisance residual ratio | 0.32956 | 0.05084 | 0.00549 |
| Metabolite-retention NRMSE | 0.38827 | 0.10178 | 0.02324 |
| Whole-spectrum NRMSE | 1.69474 | 0.27675 | 0.04024 |

Diagnostics were `nuisance_suppression_worse_than_conventional_tolerance`, `metabolite_retention_worse_than_conventional_tolerance`, and `spectral_nrmse_worse_than_conventional_tolerance`. The case demonstrates why apparent suppression or error-free file creation cannot substitute for hidden metabolite-retention evaluation.

This single generated case does not estimate prevalence and does not show that any agent condition detects or prevents the failure.
