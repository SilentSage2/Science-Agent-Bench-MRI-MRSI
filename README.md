# Science Agent Bench

Science Agent Bench is a research harness for testing which control-loop components improve small scientific-computing tasks under fixed budgets.

> **Status:** A0 benchmark contract is complete. The A1 core contracts, deterministic budget ledger, state machine, and append-only trajectory log are implemented and tested. Scientific task graders and model adapters are planned; no benchmark result is claimed yet.

## Research question

Under the same model, task, tools, token allowance, cost ceiling, retry allowance, and execution limits, do structured planning and failure-aware retry/replanning improve scientifically valid, reproducible task completion over a reactive loop?

The frozen A1 comparison will evaluate three conditions:

| Condition | Initial plan | Retry | Replan |
|---|---:|---:|---:|
| Reactive | No | No | No |
| Plan-only | Yes | No | No |
| Plan + retry/replan | Yes | Typed and bounded | Once after recoverable failure |

## Implemented foundation

- strict task, action, observation, and trajectory-event contracts;
- deterministic integer-based budget reservation and reconciliation;
- fail-closed state-transition validation;
- immutable JSONL trajectory creation with monotonic event sequences;
- SHA-256 artifact hashing;
- offline standard-library test suite.

## Planned A1 benchmark

Seven generated task families cover model fitting, uncertainty estimation, numerical convergence, spectral analysis, statistical simulation, leakage detection, and dynamical-model comparison. Each family will have public development instances and evaluator-isolated held-out instances with deterministic graders.

Task execution is not implemented yet. Model-authored code must eventually run in a disposable, network-disabled, non-root container with read-only inputs, a run-scoped output mount, and hard resource limits. A Python subprocess alone is not considered a security boundary.

## Development

Run the current offline checks without installing the package:

```bash
PYTHONPATH=src python3.12 -m unittest discover -s tests -v
```

After installing the pinned development dependencies in an isolated environment, the intended quality gate is:

```bash
ruff format --check .
ruff check .
mypy
pytest
```

## Repository boundaries

- `src/science_agent/`: provider-neutral benchmark core
- `tasks/`: public, versioned task specifications and development fixtures
- `tests/`: unit, integration, and later security-boundary tests
- `experiments/`: committed configs and compact summaries only
- `docs/`: architecture, benchmark protocol, threat model, and decisions

Generated runs, datasets, provider responses, credentials, private evaluator fixtures, and model artifacts are ignored and must not be committed.

