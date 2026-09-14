# ISMRM 2027 abstract plan

## Decision

Target a standard ISMRM abstract only if research-grade core tasks and a sensitivity-justified, frozen, paired real-model study produce an informative MR-specific result by 18 October 2026. The repository itself, reference-solver smoke test, adapter, container, abstract draft, or figures are not scientific results.

The official 2027 meeting page lists abstract submission from 1–28 October 2026 for the 8–13 May 2027 meeting in Vancouver. The detailed 2027 call is not yet publicly readable as of 14 September, so format details below use the prior standard-abstract guidance only as a planning assumption and must be rechecked when submissions open.

- [ISMRM 2027 Annual Meeting](https://www.ismrm.org/27m/)
- [ISMRM future meeting deadlines](https://www.ismrm.org/meetings-workshops/future-ismrm-meetings/)
- [Prior standard abstract guidance](https://www.ismrm.org/26m/call/standard/)

## Candidate scientific question

Under identical model, tool, token, cost, retry, and execution budgets, do agent control strategies detect or prevent technically successful but physically/statistically invalid MRI reconstruction and MRSI processing results?

Working title: **Failure-aware planning for scientifically valid autonomous MRI/MRSI experiments under fixed budgets**

The neutral wording is mandatory until the frozen paired effect supports a directional claim. The title is 99 characters under the repository validator.

The MR problem—not agent novelty—is primary: error-free execution can still violate multi-coil acquired-data physics, erase spatial detail, suppress metabolites, or endorse results under frequency/phase drift and template mismatch. Claims must remain computational and research-facing, with no diagnosis or patient-care interpretation.

## Minimum submission evidence

- Two research-grade core families: MRSI nuisance removal and undersampled MRI reconstruction. Current small generated fixtures are development tests and do not satisfy this gate.
- Realistic noise/mismatch/difficulty strata plus public/challenge-derived evaluation or literature-justified simulation ranges; MRS selection and leakage audit remain secondary unless they pass the same gate.
- An evaluator-isolated held-out set whose independent-instance count is selected by a blinded design-stage sensitivity analysis. Seeds and repeated calls are not counted as independent task instances.
- Three frozen controller conditions: reactive, plan-only, and plan plus bounded retry/replan, with budget-auditable direct and self-debug baselines.
- Conventional non-agent MR baselines, a naive method, and an oracle/sanity ceiling for each core family.
- A frozen repetition count and total run matrix derived from sensitivity, cost, and missingness planning; the earlier 72-run schedule is only a minimum pilot.
- One pinned model snapshot, prompt set, tool schema set, executor image, grader version, and budget specification.
- Separate outcomes for task success, scientific validity, reproducibility, policy violations, tokens, cost, tool calls, retries, and wall time.
- Paired instance-level analysis with uncertainty; no claim based only on aggregate pass counts.
- Failure taxonomy with representative MRI/MRSI artifacts, spectra, or reconstructions.

Additional task breadth is desirable but must not displace depth, baseline quality, domain review, or an interpretable primary interval.

## Go/no-go gates

Submit a standard abstract only if all of the following are true:

1. Live orchestration and isolated execution pass adversarial tests by 24 September.
2. Core research tools, conventional baselines, task prompts, held-out instances, graders, sample-size design, budgets, and model settings freeze by 30 September.
3. The complete frozen primary run matrix finishes with trajectories and provider usage by 10 October.
4. Analysis is reproducible from one versioned command and includes uncertainty by 14 October.
5. At least one substantive, honestly reportable outcome exists by 18 October. A well-supported null or negative result is acceptable; a harness-only result is not.
6. An MR-domain collaborator reviews task validity, figures, and claims before submission.
7. Every submitted figure passes the versioned paper-level evidence contract, statistical review, independent number verification, and rasterized SVG/PDF/PNG visual QA; no `PLANNED` or template panel is submitted as a result.
8. Title, four-part Synopsis, Impact, body, captions, figures, table, README, and conclusion resolve to the same frozen fact map and pass the versioned abstract-package validator.

If gates 1–4 fail, do not force a standard abstract. Reassess whether the 2027 call offers a registered-abstract track with rules comparable to the prior year; do not assume eligibility until the current call is public.

The pre-freeze review is operationalized in the [independent expert-review packet](../review/README.md). MRI reconstruction, MRS/MRSI, and statistical reviewers must sign against one frozen revision; the packet remains fail-closed while any critical or major issue is unresolved. A separate post-result review verifies representative failures, figures, numbers, and claims.

## Schedule

| Date | Deliverable |
|---|---|
| 14–20 Sep | Model adapter, live controller boundary, isolated executor design, abstract analysis plan |
| 21–24 Sep | End-to-end live pilot, injected-failure tests, provider usage/cost accounting |
| 25–30 Sep | Sensitivity analysis; held-out set; freeze protocol, baselines, and hashes |
| 1–10 Oct | Run the frozen comparison matrix; rerun only under predeclared failure rules |
| 11–14 Oct | Paired analysis, uncertainty, failure taxonomy, figure generation |
| 15–18 Oct | Draft title, synopsis, impact statement, body, and figures |
| 19–24 Oct | MR collaborator review and one revision cycle |
| 25–27 Oct | Submission-system validation and final proofread |
| 28 Oct | Deadline; no last-minute experimental changes |

## Abstract evidence package

This repository is one of two intended ISMRM target projects. Keep its experiment freeze, claims, figure sources, and submission QA independent; do not transfer results or panels between projects without a prospectively defined joint analysis.

Prepare one paper-level overall framework/method overview, one MR task/grader gallery, one primary paired-results figure, one efficiency/recovery figure, and one prespecified success/boundary/failure analysis. Figure 1 is not required to be an experiment plot: it must accurately show implemented inputs, core components, execution/feedback flow, outputs, and evaluation, distinguish planned elements, provide a standalone caption, and ship as an editable vector master. The empirical figures must satisfy the frozen baseline/ablation, sample-size, uncertainty, reproducibility, and visual-QA gates. The written abstract should distinguish the frozen primary comparison from pilot work and clearly state synthetic/public data provenance, limitations, and the absence of clinical claims.

The detailed five-figure layout, claim/refutation contracts, frozen sample-selection rules, uncertainty requirements, reproducible data interfaces, preview-image requirements, and visual QA gates are frozen in the [ISMRM 2027 figure specification](ISMRM_2027_FIGURES.md). Every result-dependent figure remains explicitly `PLANNED` until real frozen experiments satisfy that contract.

The [submission-facing abstract package](../abstract/README.md) contains the format/evidence contract, current structured draft, cross-artifact fact map, captions, and automated working-limit check. Its experiment-to-package table maps protocol, primary outcomes, efficiency, recovery, and failure taxonomy into Synopsis, Impact, body sections, and Figures 1–5. The [research quality audit](RESEARCH_QUALITY_AUDIT.md) supersedes any schedule-driven claim that the old 12-instance/72-run plan was automatically adequate.
