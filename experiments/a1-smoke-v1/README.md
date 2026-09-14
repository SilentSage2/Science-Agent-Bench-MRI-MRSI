# A1 scripted smoke v1

- **Date:** 2026-09-14
- **Suite:** `a1-smoke-v1`
- **Policy:** scripted reference solver
- **Research result:** no

The smoke ran `SAB-MRS-FIT-001-dev-1`, `SAB-MRI-LEAK-001-dev-1`, and `SAB-MRI-RECON-001-dev-1` once under each of the reactive, plan-only, and plan-plus-retry/replan controller paths. All nine runs passed artifact validity, numerical correctness, scientific validity, and reproducibility checks.

| Condition | Passed / attempted | Tool calls per task |
|---|---:|---:|
| Reactive | 3/3 | 1 |
| Plan-only | 3/3 | 1 |
| Plan + retry/replan | 3/3 | 1 |

For the deterministic `SAB-MRI-RECON-001-dev-1` fixture, the zero-filled inverse DFT produced sampled k-space data-consistency RMSE `6.90e-15` and image NRMSE `0.3340` against the evaluator-isolated phantom. All controller conditions use the identical reference solver, so these values are implementation checks rather than comparative research results.

This result validates shared task execution, state transitions, budget accounting, immutable trajectories, artifact hashing, and deterministic grading. Because every condition uses the same reference solver and no injected failure, it does not test the research hypotheses and must not be presented as evidence that planning or retry improves model behavior.

Reproduce with:

```bash
PYTHONPATH=src python3.12 -m science_agent.smoke --output runs/a1-smoke-v1
```
