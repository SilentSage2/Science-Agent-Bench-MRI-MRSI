# Research quality audit

Audit date: 2026-09-14  
Verdict: **RED — engineering prototype; not a publish-ready benchmark or ISMRM study**

## Executive finding

The repository currently demonstrates careful engineering: typed contracts, fail-closed budgets/state transitions, reproducible trajectories, deterministic graders, and a tested Docker boundary. Those are necessary controls, but they are not the scientific contribution. No real-model comparison, research-grade task tool, held-out benchmark set, effect estimate, uncertainty interval, or blinded MR-domain validation exists.

The defensible research direction is narrower than “Science Agent Bench for MRI/MRSI”: test **silent MR-specific scientific invalidity** and the causal effect of controller components under matched budgets. Even that claim is only potentially valuable if tasks are realistic enough to expose physics/domain failures that generic execution or exact-match benchmarks miss.

## Prior-art pressure and naming risk

- [ScienceAgentBench (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/hash/f12b4df26344f3be803c06b555252efe-Abstract-Conference.html) already evaluates 102 tasks derived from 44 peer-reviewed publications, validated by nine experts, using direct prompting, OpenHands, and self-debug. The current repository name is easily confused with that established benchmark and must not imply affiliation, extension, or novelty from the generic benchmark concept.
- [BLADE](https://arxiv.org/abs/2408.09667) already evaluates fine-grained, justifiable analytical decisions on real scientific questions and datasets, including one-shot and ReAct-style baselines.
- [MLE-bench](https://arxiv.org/abs/2410.07095) already supplies large, execution-grounded ML engineering tasks, human leaderboard baselines, and resource-scaling analysis.
- [SciAgentGym](https://sciagentgym.github.io/) already evaluates isolated multi-step scientific tool use and reports degradation with longer horizons.
- [Simple Agents Outperform Experts in Biomedical Imaging Workflow Optimization (CVPR 2026)](https://openaccess.thecvf.com/content/CVPR2026/papers/Wang_Simple_Agents_Outperform_Experts_in_Biomedical_Imaging_Workflow_Optimization_CVPR_2026_paper.pdf) directly studies agent design on production biomedical-imaging workflows with expert baselines and deployed generated functions.

Therefore, “an agent uses tools for MRI/MRSI” and “planning versus retry” are not sufficient novelty claims. Before public research positioning, use a distinct publication-facing identity (working option: `MRValidityBench`) or explicitly state that this independent project is unrelated to ICLR ScienceAgentBench. Repository renaming requires a separate decision.

## Dimension-by-dimension audit

| Dimension | Current evidence | Rating | Publication blocker |
|---|---|---:|---|
| Important, falsifiable question | Matched-budget controller question is falsifiable; silent MR validity failures could matter | Amber | Importance is asserted, not yet demonstrated on realistic MR workflows |
| Novel contribution | MR-specific validity graders are a plausible niche | Red | Strong adjacent benchmark and biomedical-imaging agent prior art; no comparative gap study or expert validation |
| Data/task realism | Four deterministic generated families with hidden references | Red | Small/toy defaults, exact synthetic templates, limited perturbations, no paper/public-challenge task provenance |
| Split/leakage control | Evaluator-only references and fixed paths are good foundations | Amber | Held-out instance manifest, contamination audit, difficulty calibration, and frozen exclusions do not exist |
| Baselines/ablations | Reactive, plan-only, retry/replan controller code exists | Red | Only scripted reference actions have run; no direct/self-debug baseline, conventional MR baseline, or human/domain calibration |
| Technical depth | Runtime, accounting, trajectory, and container boundary are substantive engineering | Amber | Scientific tools remain trusted reference solvers; Docker is not wired to research task bindings |
| Evaluation validity | Deterministic artifact and MR-specific checks exist | Amber | Threshold calibration, inter-rater/domain validation, metric gaming tests, and cross-instance robustness are missing |
| Statistical support | Paired bootstrap is planned | Red | No effect data; 12 instances/72 runs were chosen by schedule, not detectable-effect analysis |
| Failure analysis | Taxonomy and deterministic case-selection contract are planned | Red | No primary run corpus or blinded double-coding exists |
| Reproducible claims | Strong manifest/hash intent and abstract fact map | Amber | No locked research run, analysis release, or independent reproduction exists |

## Concrete weaknesses in current task depth

- MRI reconstruction defaults to a small single-coil synthetic phantom (16×16; tests often use 8×8) and zero-filled reference behavior. It does not yet test multi-coil sensitivity handling, realistic noise, acceleration/mask shifts, regularization choice, or robustness on public MR data.
- MRSI nuisance removal uses a 3×3 default grid (tests use 2×2) and nuisance templates generated from the same model used by the trusted solver. It does not yet stress frequency/phase drift, linewidth variation, template mismatch, metabolite overlap, spatial heterogeneity, or realistic complex spectra.
- MRS basis selection uses a small generated regression problem. It does not yet represent basis mismatch, linewidth/phase/frequency nuisance, correlated metabolites, macromolecules, uncertainty, or accepted spectroscopy fitting baselines.
- Leakage audit uses a small generated table with directly seeded violations. It is useful for correctness tests but insufficient evidence that an agent can detect realistic subject/session/acquisition/temporal leakage in MR studies.

These tasks remain valuable unit-test fixtures. They must not be described as research-grade benchmark instances.

## Minimum defensible pivot

### Contribution

Position the work as a preregistered pilot of MR-specific scientific-validity failures, not a new general scientific agent or a claim of autonomous discovery. The contribution must be one or more of:

1. evaluator-isolated MRI/MRSI tasks where executable or plausible outputs can still violate physics/statistics;
2. a validated taxonomy and grader suite for those silent failures;
3. a matched-budget causal ablation showing when planning/recovery helps, does nothing, or harms validity and efficiency.

### Task evidence gate

Before primary runs, at least two core families—MRI reconstruction and MRSI nuisance removal—must pass all of the following:

- meaningful algorithm choices rather than access to a reference answer;
- realistic dimensions, noise, mismatch, and difficulty strata;
- at least one appropriately licensed public/challenge-derived evaluation route or a simulator whose parameter ranges are justified from MR literature;
- a conventional non-agent MR baseline, a naive baseline, and an oracle/sanity ceiling;
- adversarial metric-gaming and hidden-reference leakage tests;
- written review by an MRI/MRS domain expert.

MRS model selection and leakage audit may remain secondary diagnostic families unless they reach the same gate.

### Agent baselines

The primary controller ablation may retain reactive, plan-only, and bounded retry/replan under identical model/tool/budget settings. To establish competitiveness rather than only internal causality, add:

- one-shot/direct generation with no iterative observation;
- a budget-matched self-debug baseline comparable in spirit to prior scientific-agent work;
- task-level conventional MR and oracle references, clearly separated from agent baselines.

Do not claim superiority to experts without an actual blinded expert baseline. Do not compare conditions with unequal effective model or tool budgets without reporting the inequality.

### Sample size and analysis

Treat the earlier 12-instance/72-run schedule as a **minimum pilot**, not a confirmatory design. Before freezing `n`, run a blinded design-stage sensitivity analysis over plausible paired discordance/effect ranges and set the number of independent instances accordingly. Seeds are repetitions, not independent task samples. If time or cost cannot support the resulting design, narrow the claim to feasibility and descriptive failure characterization.

Report paired absolute effects, 95% intervals, raw instance outcomes, task-family heterogeneity, missingness, cost, and all negative/adverse results. A null result is acceptable if the interval and design are informative.

## Stop/go criteria

The project is worth an ISMRM submission only if, by the preregistered go/no-go date:

1. two or more core MR families pass the task evidence gate;
2. a domain reviewer judges the failure modes scientifically meaningful;
3. direct, self-debug, reactive, plan-only, and retry/replan comparisons are budget-auditable;
4. sample-size sensitivity and the frozen analysis support an interpretable interval;
5. real primary results reveal a substantive MR-validity, efficiency, or failure-mode finding, including a rigorous negative result.

Otherwise, publish the repository only as an engineering prototype, remove directional abstract language, and defer the conference claim rather than filling figures or prose.

## Evidence required for a credible public/recruiting release

A reviewer or recruiter should be able to inspect concrete evidence—not polish—showing:

- at least two non-toy MRI/MRSI task implementations with documented domain decisions and strong conventional baselines;
- held-out, leakage-audited instances and evaluator-isolated references;
- a real-model, matched-budget comparison with immutable trajectories and complete cost/usage;
- effect sizes and uncertainty, not just pass counts;
- reproducible examples of silent scientific failure and deterministic case selection;
- independent MR-domain and numeric review;
- one-command reproduction of analysis and figures from the frozen release manifest.

Until those artifacts exist, the honest value proposition is “careful benchmark infrastructure and a testable MR research plan,” not “publish-ready MRI/MRSI agent research.”
