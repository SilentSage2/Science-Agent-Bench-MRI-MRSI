# Independent MR protocol review

This packet is the mandatory pre-freeze review for the MRI/MRSI agent study. It
does not certify clinical use and it is not evidence that the controller
comparison is ready. Reviewers assess the computational MR task, hidden grading,
experimental design, and claims before held-out instances or primary outcomes are
released.

## Required reviewers

At least three independent people must review the packet:

1. an MRI reconstruction expert with multi-coil Cartesian reconstruction
   experience;
2. an MRS/MRSI expert with spectral preprocessing or quantification experience;
3. a statistician or evaluation-methods reviewer familiar with paired and
   clustered experiments.

An agent-evaluation reviewer is strongly recommended for the controller
semantics. One person may not sign more than one of the three required roles.
Every reviewer must disclose conflicts and state the parts they are qualified to
assess.

## Review sequence

1. Read [PROTOCOL_V1.md](PROTOCOL_V1.md), the source files listed in
   [REVIEW_PACKET_MANIFEST.json](REVIEW_PACKET_MANIFEST.json), and the relevant
   domain form.
2. Reproduce the committed baseline summaries and one hidden endpoint case using
   the commands in the experiment records.
3. Record findings in [ISSUE_LOG.md](ISSUE_LOG.md). Critical and major issues must
   have an owner, proposed resolution, and verification evidence.
4. Complete the MRI, MRSI, statistical, and controller forms. A reviewer may mark
   an item `Not qualified`; it must then be assessed by another reviewer.
5. After revisions, reviewers complete [SIGNOFF.md](SIGNOFF.md) against one exact
   source revision and executor image digest.

## Decision rule

The primary run is **NO-GO** unless all of the following are true:

- the MRI, MRSI, and statistical reviewers select `Accept` or
  `Accept with required revisions`, and every required revision is verified;
- no critical issue and no unresolved major issue remains;
- direct and reactive have measurably distinct, prospectively specified
  mechanics;
- self-debug can inspect and revise a technically successful candidate without
  access to hidden scores;
- independent task-instance counts, repetition counts, missingness rules,
  estimands, intervals, and multiplicity handling are frozen before outcomes;
- instance manifests, prompts, schemas, graders, analysis, model snapshot,
  budgets, pricing basis, and executor digest are hashed and immutable;
- both MR reviewers approve the simulation ranges, conventional baselines,
  validity thresholds, and representative boundary cases;
- the figure-data contract and independent number-check workflow are executable.

The present packet starts in `NO-GO`. Blank forms and unsigned placeholders are
not approvals. Pilot results may inform engineering but may not be used to tune
held-out thresholds or select favorable primary endpoints.

