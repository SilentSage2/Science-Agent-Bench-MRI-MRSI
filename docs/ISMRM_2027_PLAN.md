# ISMRM 2027 abstract plan

## Decision

Target a standard ISMRM abstract only if the benchmark produces frozen, paired real-model results by 18 October 2026. The repository itself, reference-solver smoke test, or adapter implementation is not a scientific result.

The official 2027 meeting page lists abstract submission from 1–28 October 2026 for the 8–13 May 2027 meeting in Vancouver. The detailed 2027 call is not yet publicly readable as of 14 September, so format details below use the prior standard-abstract guidance only as a planning assumption and must be rechecked when submissions open.

- [ISMRM 2027 Annual Meeting](https://www.ismrm.org/27m/)
- [ISMRM future meeting deadlines](https://www.ismrm.org/meetings-workshops/future-ismrm-meetings/)
- [Prior standard abstract guidance](https://www.ismrm.org/26m/call/standard/)

## Candidate scientific question

Under identical model, task, tool, token, cost, retry, and execution budgets, do structured planning and one failure-aware replan improve scientifically valid completion of MRI/MRSI computational experiments over a reactive agent?

Candidate title: **Failure-aware planning improves the validity of autonomous MRI/MRSI computational experiments under fixed budgets**

This framing makes the contribution an MR research-methods study rather than a generic agent demo. Claims must remain computational and research-facing, with no diagnosis or patient-care interpretation.

## Minimum submission dataset

- Four frozen MR-specific task families already implemented: MRS basis-model selection, MRSI nuisance removal, MRI/MRSI leakage audit, and undersampled MRI reconstruction.
- Three evaluator-isolated held-out instances per family.
- Three frozen controller conditions: reactive, plan-only, and plan plus bounded retry/replan.
- Two independent repetitions for every condition-instance pair: 72 primary runs total.
- One pinned model snapshot, prompt set, tool schema set, executor image, grader version, and budget specification.
- Separate outcomes for task success, scientific validity, reproducibility, policy violations, tokens, cost, tool calls, retries, and wall time.
- Paired instance-level analysis with uncertainty; no claim based only on aggregate pass counts.
- Failure taxonomy with representative MRI/MRSI artifacts, spectra, or reconstructions.

The remaining three planned task families are desirable but not required for the first abstract. Adding breadth must not delay a reproducible four-family experiment.

## Go/no-go gates

Submit a standard abstract only if all of the following are true:

1. Live orchestration and isolated execution pass adversarial tests by 24 September.
2. Task prompts, held-out instances, graders, budgets, and model settings freeze by 30 September.
3. All 72 primary runs finish with complete trajectories and provider usage by 10 October.
4. Analysis is reproducible from one versioned command and includes uncertainty by 14 October.
5. At least one substantive, honestly reportable outcome exists by 18 October. A well-supported null or negative result is acceptable; a harness-only result is not.
6. An MR-domain collaborator reviews task validity, figures, and claims before submission.
7. Every submitted figure passes the versioned paper-level evidence contract, statistical review, independent number verification, and rasterized SVG/PDF/PNG visual QA; no `PLANNED` or template panel is submitted as a result.

If gates 1–4 fail, do not force a standard abstract. Reassess whether the 2027 call offers a registered-abstract track with rules comparable to the prior year; do not assume eligibility until the current call is public.

## Schedule

| Date | Deliverable |
|---|---|
| 14–20 Sep | Model adapter, live controller boundary, isolated executor design, abstract analysis plan |
| 21–24 Sep | End-to-end live pilot, injected-failure tests, provider usage/cost accounting |
| 25–30 Sep | Three held-out instances per family; freeze protocol and hashes |
| 1–10 Oct | Run the 72-run comparison; rerun only under predeclared failure rules |
| 11–14 Oct | Paired analysis, uncertainty, failure taxonomy, figure generation |
| 15–18 Oct | Draft title, synopsis, impact statement, body, and figures |
| 19–24 Oct | MR collaborator review and one revision cycle |
| 25–27 Oct | Submission-system validation and final proofread |
| 28 Oct | Deadline; no last-minute experimental changes |

## Abstract evidence package

Prepare one primary paired-results figure, one cost/efficiency figure, one MRI reconstruction example, one MRSI spectrum example, and one compact failure-taxonomy panel. The written abstract should distinguish the frozen primary comparison from pilot work and clearly state synthetic/public data provenance, limitations, and the absence of clinical claims.

The detailed five-figure layout, claim/refutation contracts, frozen sample-selection rules, uncertainty requirements, reproducible data interfaces, preview-image requirements, and visual QA gates are frozen in the [ISMRM 2027 figure specification](ISMRM_2027_FIGURES.md). Every result-dependent figure remains explicitly `PLANNED` until real frozen experiments satisfy that contract.
