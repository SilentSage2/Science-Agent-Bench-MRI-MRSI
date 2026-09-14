# Complex MRSI nuisance-removal baseline pilot v1

Status: **task-calibration evidence, not an agent or conference result**
Date: 2026-09-14

## Question

Does a complex-spectrum task with frequency/phase drift, baseline variation, lineshape mismatch, and noise distinguish adaptive nuisance modeling from fixed-template projection while independently measuring metabolite retention?

## Frozen setup

- 4×4 voxel grids with 256 complex spectral points from 0.5–5.0 ppm;
- NAA-, creatine-, choline-, and Glx-like metabolite components;
- spatially varying water/lipid amplitudes, frequency and phase drift, mixed Gaussian/Lorentzian mismatch, complex polynomial baseline, and complex noise;
- easy, moderate, and hard stress strata with three deterministic generator cases each;
- naive baseline: fixed nominal water/lipid projection;
- conventional baseline: bounded shift/width search with mixed-lineshape and first-order phase bases;
- oracle: evaluator-only subtraction of the true nuisance and baseline components;
- paired case bootstrap: 10,000 resamples, seed 20270915.

## Result

| Difficulty | Fixed nuisance residual | Adaptive nuisance residual | Fixed metabolite-retention NRMSE | Adaptive metabolite-retention NRMSE | Fixed spectral NRMSE | Adaptive spectral NRMSE |
|---|---:|---:|---:|---:|---:|---:|
| Easy | 0.212324 | 0.047164 | 0.264101 | 0.080848 | 1.085980 | 0.247639 |
| Moderate | 0.254052 | 0.049635 | 0.311947 | 0.093667 | 1.307512 | 0.266389 |
| Hard | 0.322791 | 0.050987 | 0.384760 | 0.126263 | 1.666200 | 0.290976 |

Adaptive projection improved spectral NRMSE in 9/9 cases. The mean paired reduction was 1.08490 with a seed-fixed case-bootstrap 95% interval of [0.94404, 1.23455]. Hidden grading keeps nuisance residual, metabolite retention, and whole-spectrum error separate so strong suppression cannot compensate for metabolite attenuation.

These generated cases are mechanism/calibration units, not independent biological subjects. Voxels and generator seeds must not be promoted to independent sample size. No model or agent was evaluated.

## Reproduction

```bash
PYTHONPATH=src python3.12 -m science_agent.mrsi_nuisance_pilot \
  --output runs/mrsi-complex-nuisance-baseline-pilot-v1
```
