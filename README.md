# Science Agent Bench MRI/MRSI

Science Agent Bench MRI/MRSI is a provider-neutral research prototype for measuring when technically successful agent/tool workflows still produce physically or statistically invalid MR results, and whether control strategies detect or prevent those failures under fixed budgets.

This independent prototype is not affiliated with the ICLR 2025 benchmark named [ScienceAgentBench](https://proceedings.iclr.cc/paper_files/paper/2025/hash/f12b4df26344f3be803c06b555252efe-Abstract-Conference.html). A distinct publication-facing name is required before a research release to avoid confusion.

> **Status:** Engineering/research prototype, not a benchmark release. Two generated research-core families now have naive/conventional/oracle baselines, hidden graders, fixed-path Docker bindings, and frozen development manifests. A 10-cell real-model development checkout exposed silent invalidity and control-design defects but is not a primary result. Public/challenge validation, an independently sized primary set, a frozen real-model comparison, and MR-domain review do not yet exist.

## Research question

Under the same model, MRI/MRSI task, tools, token allowance, cost ceiling, retry allowance, and execution limits, do agent control strategies detect or prevent technically successful but scientifically invalid MRI reconstruction and MRSI processing results?

The benchmark measures computational research workflows, not clinical diagnosis. Initial tasks use generated phantoms, spectra, metadata, and known reference parameters so that grading remains deterministic and no private clinical data is required.

The primary comparison is designed around five conditions:

| Condition | Initial plan | Retry | Replan |
|---|---:|---:|---:|
| Direct | No | No | No |
| Self-debug | No | One observation-conditioned retry | No structured replan |
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
- a research-candidate noisy multi-coil Cartesian MRI task with complex coil sensitivities, variable-density masks, and naive/conventional/oracle baselines;
- a research-candidate complex MRSI task with frequency/phase drift, mixed-lineshape mismatch, complex baseline/noise, and separate nuisance-retention grading;
- a provider-neutral model protocol and fail-closed OpenAI Responses API adapter;
- an end-to-end single-agent controller with direct, self-debug, reactive, plan-only, and bounded retry/replan paths;
- an explicit allowlisted tool registry with reservation-before-execution accounting;
- a digest-pinned Docker executor with denied network, read-only inputs/runtime, non-root execution, resource ceilings, bounded output, and artifact validation;
- fixed-path development bindings from all four task families through artifacts and graders;
- independent deterministic graders with positive and adversarial fixtures;
- a 20-run smoke across five controller conditions;
- a separate 20-run agent-pipeline smoke across every controller and development task family;
- a 10-run scripted research dry-run crossing five conditions with the MRI and MRSI research bindings;
- an adversarial controller-discrimination replay in which direct, self-debug, reactive, plan-only, and retry/replan have distinct enforced trajectory signatures;
- a private-keyed, sensitivity-sized primary-manifest generator that enforces 122 unique dependence groups without publishing evaluator seeds;
- family-stratified paired analysis with instance-cluster bootstrap intervals, exact sign-flip sensitivity, explicit exclusions, and fail-closed Figure 3/4 data status;
- a metadata-only public-source ingestion smoke with license/access, mapping, integrity, containment, and split-leakage checks;
- offline standard-library test suite.

## Planned A1 benchmark

Seven generated task families cover MRS basis fitting, MRSI nuisance removal, undersampled MRI reconstruction, reconstruction quality control, spectral/metabolite quantification, subject-level leakage detection, and dynamic MR model comparison. Each family will have public development instances and evaluator-isolated held-out instances with deterministic graders.

The two depth-target families and their research bindings are implemented on generated data. Three secondary task families, public/challenge validation, an independently sized held-out suite, and domain review remain planned. No paid model request or real control-loop comparison has run. Reference and scripted tools prove orchestration only and are excluded from research results. Model-authored code remains disabled; the research tools execute only allowlisted repository-owned algorithms inside the Docker boundary.

The [research quality audit](docs/RESEARCH_QUALITY_AUDIT.md) is a binding red-team assessment. It identifies prior-art and naming risk, toy-task limitations, missing direct/self-debug and conventional MR baselines, absent sample-size justification, and the minimum evidence required before an ISMRM or publish-ready claim.

The first substantive calibration result is deliberately narrow: in a frozen nine-case synthetic multi-coil pilot, regularized SENSE-CG improved magnitude NRMSE over zero fill in 9/9 cases (mean paired reduction 0.0661; seed-fixed bootstrap 95% interval [0.0519, 0.0806]). This validates task separation, not agent performance or clinical realism. The [pilot record](experiments/mri-multicoil-baseline-pilot-v1/README.md) includes the hard-stratum degradation and reproduction command. A separate [design sensitivity](experiments/design-sensitivity-v1/README.md) shows why the old 12-instance plan cannot be treated as confirmatory.

A containerized mechanism case now demonstrates the core endpoint: zero fill returned a successful tool observation and valid, reproducible artifacts, but hidden multi-coil grading rejected its magnitude and gradient fidelity relative to SENSE-CG. The [silent-invalidity record](experiments/mri-silent-invalidity-endpoint-v1/README.md) is evidence that execution success and MR validity can diverge; it is not an agent-effect estimate.

The second depth target shows the same mechanism in spectroscopy. Across nine generated MRSI calibration cases, adaptive drift/lineshape modeling improved spectral NRMSE over fixed projection in 9/9 cases (mean paired reduction 1.0849; case-bootstrap 95% interval [0.9440, 1.2345]). A hard fixed-template case completed normally but failed hidden nuisance, metabolite-retention, and spectral criteria. See the [MRSI pilot](experiments/mrsi-complex-nuisance-baseline-pilot-v1/README.md) and [endpoint record](experiments/mrsi-silent-invalidity-endpoint-v1/README.md). Neither is an agent result.

A paid two-instance development checkout reached hidden evaluation in 10/10 cells and found four technically complete MRI outputs that failed hidden fidelity while being endorsed as valid; all five MRSI cells passed. Because there is only one instance per family and the five-condition contrast remains confounded, the run was stopped rather than expanded. The [v4 record](experiments/real-model-development-pilot-v4/README.md) reports complete denominators, costs, and limitations; none of its condition counts enter the abstract.

## Current smoke result

| Policy | Tasks passed | Purpose |
|---|---:|---|
| Scripted direct | 4/4 | One-shot development binding |
| Scripted self-debug | 4/4 | Successful-candidate revision or failure-retry development binding |
| Scripted reactive | 4/4 | MRS fit + MRSI nuisance + MRI leakage/reconstruction |
| Scripted plan-only | 4/4 | MRS fit + MRSI nuisance + MRI leakage/reconstruction |
| Scripted plan + retry/replan | 4/4 | MRS fit + MRSI nuisance + MRI leakage/reconstruction |

These are reference-solver runs, not evidence that one control strategy is better. The committed [smoke summary](experiments/a1-smoke-v1/README.md) records the protocol and limitations.
The separate [agent-pipeline smoke summary](experiments/a1-agent-smoke-v1/README.md) records fixed-path binding validation and its non-research status. The research-grade crossing is reproducible with `sab-research-dry-run`, which requires an explicit `--acknowledge-non-model` flag.

## Development

Run the current offline checks without installing the package:

```bash
PYTHONPATH=src python3.12 -m unittest discover -s tests -v
```

Run the end-to-end smoke into a new immutable directory:

```bash
PYTHONPATH=src python3.12 -m science_agent.smoke --output runs/a1-smoke-v1
```

Run the real agent/controller path with deterministic development bindings:

```bash
PYTHONPATH=src python3.12 -m science_agent.agent_smoke --output runs/a1-agent-smoke-v1
```

After installing the pinned development dependencies in an isolated environment, the intended quality gate is:

```bash
ruff format --check .
ruff check .
mypy
pytest
```

The Docker security integration tests are opt-in because ordinary CI runners may not expose a Docker daemon:

```bash
SAB_RUN_DOCKER_TESTS=1 PYTHONPATH=src pytest tests/test_container_executor.py
```

## Repository boundaries

- `src/science_agent/`: provider-neutral benchmark core
- `tasks/`: public, versioned task specifications and development fixtures
- `tests/`: unit, integration, and later security-boundary tests
- `experiments/`: committed configs and compact summaries only
- `docs/`: architecture, benchmark protocol, threat model, and decisions

See [model adapters](docs/MODEL_ADAPTERS.md) for the provider boundary, credential rules, and live-run requirements.
See the [credential-gated pilot runbook](docs/LIVE_PILOT_RUNBOOK.md) for the safe key workflow, current cost ceiling, and reproducible launch command.
See the [agent runtime](docs/AGENT_RUNTIME.md) for controller semantics, accounting invariants, and the current isolation boundary.
The [independent expert-review packet](review/README.md) turns the MRI, MRSI, statistical, and controller pre-freeze checks into versioned forms, an issue log, and a fail-closed signoff. Its current status is `NO-GO` until the documented control-design and sample-size issues are resolved and independently approved.
The [public/challenge validity plan](docs/PUBLIC_VALIDITY_PLAN.md) prospectively separates external mechanism checks from synthetic hidden-component endpoints and forbids redistribution of agreement-controlled MR data.
The [ISMRM 2027 abstract plan](docs/ISMRM_2027_PLAN.md) defines sensitivity-justified experiment and submission gates; the earlier 72-run schedule is only a pilot floor and no completed research result is claimed.
The [conference figure specification](docs/ISMRM_2027_FIGURES.md) defines five review figures, a separate preview image, immutable plotting inputs, and visual/scientific QA gates.
The [complete abstract package](abstract/README.md) provides the 2026-format working draft, evidence contract, cross-artifact fact lock, five captions, and an automated length validator. It remains explicitly `PLANNED` until frozen real-model results exist.

Generated runs, datasets, provider responses, credentials, private evaluator fixtures, and model artifacts are ignored and must not be committed.

## Data direction

The default suite remains fully generated and redistributable. Later optional adapters may support the [ISMRM MRS Fitting Challenge](https://www.ismrm.org/workshops/Spectroscopy16/mrs_fitting_challenge/) and appropriately licensed datasets cataloged by [MRSHub](https://mrshub.org/datasets_mrsi/). NYU fastMRI requires individual agreement and prohibits redistribution, so the repository will provide an adapter and integrity instructions only—never data or derived files.
