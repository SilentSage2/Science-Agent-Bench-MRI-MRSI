# A1 scripted smoke v1

- **Date:** 2026-09-14
- **Suite:** `a1-smoke-v1`
- **Policy:** scripted reference solver
- **Research result:** no

The smoke ran `SAB-MRS-FIT-001-dev-1`, `SAB-MRSI-NUIS-001-dev-1`, `SAB-MRI-LEAK-001-dev-1`, and `SAB-MRI-RECON-001-dev-1` once under each of the reactive, plan-only, and plan-plus-retry/replan controller paths. All 12 runs passed artifact validity, numerical correctness, scientific validity, and reproducibility checks.

| Condition | Passed / attempted | Tool calls per task |
|---|---:|---:|
| Reactive | 4/4 | 1 |
| Plan-only | 4/4 | 1 |
| Plan + retry/replan | 4/4 | 1 |

For the deterministic `SAB-MRI-RECON-001-dev-1` fixture, the zero-filled inverse DFT produced sampled k-space data-consistency RMSE `6.90e-15` and image NRMSE `0.3340` against the evaluator-isolated phantom. All controller conditions use the identical reference solver, so these values are implementation checks rather than comparative research results.

For `SAB-MRSI-NUIS-001-dev-1`, joint template projection produced mean water suppression of `249.74 dB`, mean lipid suppression of `244.10 dB`, and metabolite-retention NRMSE `0.1889` against evaluator-only clean spectra. The very high suppression values are expected for a synthetic fixture generated from the exact public nuisance templates; shifted and mismatched templates belong in later robustness instances.

This result validates shared task execution, state transitions, budget accounting, immutable trajectories, artifact hashing, and deterministic grading. Because every condition uses the same reference solver and no injected failure, it does not test the research hypotheses and must not be presented as evidence that planning or retry improves model behavior.

Reproduce with:

```bash
PYTHONPATH=src python3.12 -m science_agent.smoke --output runs/a1-smoke-v1
```
