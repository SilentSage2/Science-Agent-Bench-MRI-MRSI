# MRI silent-invalidity endpoint validation v1

Status: **endpoint/mechanism validation, not a real-model comparison**  
Date: 2026-09-14

## MR question

Can a reconstruction tool return normally, produce schema-valid reproducible artifacts, and report completion while the reconstruction is scientifically inferior under hidden multi-coil fidelity checks?

## Frozen case

- task: `SAB-MRI-RECON-MC-001`;
- 32×32 complex phantom, four coils, R=6 variable-density mask, relative complex-noise level 0.02;
- seed 1301, retained only for this endpoint fixture;
- reconstruction: zero-filled multi-coil adjoint;
- container controls: no network, read-only root/input, non-root, dropped capabilities, hard resources;
- research image: `sha256:83f2faaf0f3e7556b29867b343e75448fe5bd3c4028d486b84439aa5676d1e84`;
- hidden comparison: fixed SENSE-CG conventional baseline, λ=0.003, 40 iterations.

## Result

The Docker tool observation was successful (`reconstruction_artifacts_created`). The artifacts were schema-valid, numerically self-consistent, and reproducible. Nevertheless, the hidden grader marked scientific validity false:

| Metric | Zero-filled output | Conventional SENSE-CG |
|---|---:|---:|
| Magnitude NRMSE | 0.37294 | 0.29148 |
| Gradient NRMSE | 0.89280 | 0.80058 |
| Sampled k-space residual | 0.07836 | 0.01587 |

Diagnostics were `magnitude_nrmse_worse_than_conventional_tolerance` and `gradient_nrmse_worse_than_conventional_tolerance`. Thus, ordinary execution success would have accepted a materially worse MR result, while the evaluator-isolated domain check detected it.

This is one synthetic mechanism case, not an estimate of silent-invalidity prevalence and not evidence that any controller prevents it. It validates the distinction among technical completion, scientific validity, and agent recognition that the real-model pilot will measure.
