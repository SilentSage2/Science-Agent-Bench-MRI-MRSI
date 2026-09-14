# Science Agent Bench MRI/MRSI

Science Agent Bench is a provider-neutral research harness for testing which control-loop components improve MRI and MR spectroscopic imaging (MRSI) experiments under fixed budgets.

> **Status:** A0 benchmark contract is complete. The A1 core, four deterministic task families, and first replaceable real-model adapter are implemented and tested. The 12/12 scripted smoke result validates the harness only; no real-model research result is claimed yet.

## Research question

Under the same model, MRI/MRSI task, tools, token allowance, cost ceiling, retry allowance, and execution limits, do structured planning and failure-aware retry/replanning improve scientifically valid, reproducible experiment completion over a reactive loop?

The benchmark measures computational research workflows, not clinical diagnosis. Initial tasks use generated phantoms, spectra, metadata, and known reference parameters so that grading remains deterministic and no private clinical data is required.

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
- synthetic MRS basis-model selection, MRSI nuisance removal, MRI/MRSI split-leakage, and undersampled MRI reconstruction tasks;
- a provider-neutral model protocol and fail-closed OpenAI Responses API adapter;
- an end-to-end single-agent controller with frozen reactive, plan-only, and bounded retry/replan conditions;
- an explicit allowlisted tool registry with reservation-before-execution accounting;
- independent deterministic graders with positive and adversarial fixtures;
- a 12-run smoke across all three controller conditions;
- offline standard-library test suite.

## Planned A1 benchmark

Seven generated task families cover MRS basis fitting, MRSI nuisance removal, undersampled MRI reconstruction, reconstruction quality control, spectral/metabolite quantification, subject-level leakage detection, and dynamic MR model comparison. Each family will have public development instances and evaluator-isolated held-out instances with deterministic graders.

Three task families, production MRI/MRSI tool bindings, and isolated task execution remain planned. The single-agent control loop and first adapter are offline-tested, but no paid model request or control-loop comparison has been run. Model-authored code must eventually run in a disposable, network-disabled, non-root container with read-only inputs, a run-scoped output mount, and hard resource limits. A Python subprocess alone is not considered a security boundary.

## Current smoke result

| Policy | Tasks passed | Purpose |
|---|---:|---|
| Scripted reactive | 4/4 | MRS fit + MRSI nuisance + MRI leakage/reconstruction |
| Scripted plan-only | 4/4 | MRS fit + MRSI nuisance + MRI leakage/reconstruction |
| Scripted plan + retry/replan | 4/4 | MRS fit + MRSI nuisance + MRI leakage/reconstruction |

These are reference-solver runs, not evidence that one control strategy is better. The committed [smoke summary](experiments/a1-smoke-v1/README.md) records the protocol and limitations.

## Development

Run the current offline checks without installing the package:

```bash
PYTHONPATH=src python3.12 -m unittest discover -s tests -v
```

Run the end-to-end smoke into a new immutable directory:

```bash
PYTHONPATH=src python3.12 -m science_agent.smoke --output runs/a1-smoke-v1
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

See [model adapters](docs/MODEL_ADAPTERS.md) for the provider boundary, credential rules, and live-run requirements.
See the [agent runtime](docs/AGENT_RUNTIME.md) for controller semantics, accounting invariants, and the current isolation boundary.
The [ISMRM 2027 abstract plan](docs/ISMRM_2027_PLAN.md) defines a time-bounded 72-run experiment and explicit submission gates; it does not claim acceptance or completed research results.
The [conference figure specification](docs/ISMRM_2027_FIGURES.md) defines five review figures, a separate preview image, immutable plotting inputs, and visual/scientific QA gates.

Generated runs, datasets, provider responses, credentials, private evaluator fixtures, and model artifacts are ignored and must not be committed.

## Data direction

The default suite remains fully generated and redistributable. Later optional adapters may support the [ISMRM MRS Fitting Challenge](https://www.ismrm.org/workshops/Spectroscopy16/mrs_fitting_challenge/) and appropriately licensed datasets cataloged by [MRSHub](https://mrshub.org/datasets_mrsi/). NYU fastMRI requires individual agreement and prohibits redistribution, so the repository will provide an adapter and integrity instructions only—never data or derived files.
