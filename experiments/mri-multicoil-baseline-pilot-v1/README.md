# Multi-coil MRI baseline pilot v1

Status: **task-calibration evidence, not an agent or conference result**  
Date: 2026-09-14

## Question

Does the candidate task distinguish a conventional regularized parallel-imaging reconstruction from a naive zero-filled adjoint across prespecified acceleration/noise strata?

## Frozen setup

- 64×64 complex phantoms with three seeded small structures;
- eight smooth complex coil-sensitivity maps normalized in root-sum-of-squares power;
- centered variable-density Cartesian phase-encode masks;
- complex Gaussian acquisition noise scaled to sampled-k-space RMS;
- easy: R=4, relative noise=0.01;
- medium: R=6, relative noise=0.02;
- hard: R=8, relative noise=0.04;
- seeds: 1101, 1102, 1103 per stratum;
- naive baseline: zero-filled multi-coil adjoint;
- conventional baseline: SENSE normal equation with finite-difference regularization λ=0.003 and 40 conjugate-gradient iterations;
- oracle: evaluator-only complex reference;
- paired bootstrap: 10,000 resamples, seed 20270914.

## Result

| Difficulty | Zero-fill magnitude NRMSE | SENSE-CG magnitude NRMSE | Zero-fill gradient NRMSE | SENSE-CG gradient NRMSE | SENSE-CG sampled residual |
|---|---:|---:|---:|---:|---:|
| Easy | 0.252989 | 0.161967 | 0.750664 | 0.565932 | 0.010401 |
| Medium | 0.286715 | 0.218128 | 0.824283 | 0.710669 | 0.018359 |
| Hard | 0.303364 | 0.264659 | 0.868029 | 0.828945 | 0.036643 |

SENSE-CG improved magnitude NRMSE in 9/9 cases. The mean paired reduction was 0.06610 with a seed-fixed case-bootstrap 95% interval of [0.05186, 0.08060]. Separation narrowed at the hardest stratum, which is retained rather than tuned away.

This establishes only that the simulator and metrics distinguish two algorithms. The nine generated cases are not independent clinical samples, the simulator ranges are not yet literature-validated, and no agent was evaluated. The task remains a research candidate until public/challenge validation, metric-gaming tests, Docker binding, and MR-domain review pass.

## Reproduction

```bash
PYTHONPATH=src python3.12 -m science_agent.mri_recon_pilot \
  --output runs/mri-multicoil-baseline-pilot-v1
```
