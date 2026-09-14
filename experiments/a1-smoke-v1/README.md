# A1 scripted smoke v1

- **Date:** 2026-09-14
- **Suite:** `a1-smoke-v1`
- **Policy:** scripted reference solver
- **Research result:** no

The smoke ran `SAB-MRS-FIT-001-dev-1` and `SAB-MRI-LEAK-001-dev-1` once under each of the reactive, plan-only, and plan-plus-retry/replan controller paths. All six runs passed artifact validity, numerical correctness, scientific validity, and reproducibility checks.

| Condition | Passed / attempted | Tool calls per task |
|---|---:|---:|
| Reactive | 2/2 | 1 |
| Plan-only | 2/2 | 1 |
| Plan + retry/replan | 2/2 | 1 |

This result validates shared task execution, state transitions, budget accounting, immutable trajectories, artifact hashing, and deterministic grading. Because every condition uses the same reference solver and no injected failure, it does not test the research hypotheses and must not be presented as evidence that planning or retry improves model behavior.

Reproduce with:

```bash
PYTHONPATH=src python3.12 -m science_agent.smoke --output runs/a1-smoke-v1
```
