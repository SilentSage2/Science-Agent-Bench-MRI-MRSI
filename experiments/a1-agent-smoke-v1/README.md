# A1 agent-pipeline smoke v1

## Purpose

Validate the complete offline path from a scripted model action through `MRIScienceAgent`, the fixed-path task tool, artifact generation, deterministic grading, budget accounting, run manifest, and append-only trajectory. This is infrastructure validation, not a model comparison or research result.

## Frozen setup

- Git commit: recorded by the repository commit containing this summary
- Model: `scripted-reference-v1`
- Controllers: reactive, plan-only, plan plus retry/replan
- Tasks: `SAB-MRS-FIT-001`, `SAB-MRI-LEAK-001`, `SAB-MRI-RECON-001`, `SAB-MRSI-NUIS-001`
- Instances: one generated development fixture per task
- Tools: fixed-path reference bindings with no model-controlled arguments
- Evaluators: independent deterministic graders

## Result

| Controller | Successful tasks | Model calls per task | Tool calls per task |
|---|---:|---:|---:|
| Reactive | 4/4 | 2 | 1 |
| Plan-only | 4/4 | 3 | 1 |
| Plan + retry/replan | 4/4 | 3 | 1 |

Overall: **12/12 pipeline runs succeeded**.

The retry/replan controller did not encounter an injected failure in this smoke. Its recovery path is covered separately by unit tests. Equal success is expected because every controller receives a scripted action sequence and reference tool; the result does not support a controller-effect claim.

## Reproduction

```bash
PYTHONPATH=src python3.12 -m science_agent.agent_smoke \
  --output runs/a1-agent-smoke-v1
```

The output path must not already exist. Generated runs remain ignored because they contain verbose trajectories and task artifacts; this compact summary is the committed record.

