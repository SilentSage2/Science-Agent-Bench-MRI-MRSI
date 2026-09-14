# Agent-control semantics review

Reviewer: `UNASSIGNED`  
Date: `UNASSIGNED`  
Source revision reviewed: `UNASSIGNED`

| Item | Decision | Evidence / issue |
|---|---|---|
| Direct and reactive are behaviorally distinct and testable | UNREVIEWED | Implemented in protocol v1.1; `DIRECT-PRECOMMIT-001`, `REACTIVE-OBSERVE-001` |
| Self-debug can audit a successful candidate without hidden feedback | UNREVIEWED | `SELFDEBUG-SUCCESS-REVISION-001`; hidden-score flag false |
| Planning and replanning schemas expose only condition-authorized actions | UNREVIEWED | phase schema tests in `tests/test_agent.py` |
| Model, task, tools and hard budgets are matched except for the declared intervention | UNREVIEWED | `protocol/five_condition_protocol_v1.json`; live-pilot budget test |
| Retry/replan eligibility and failure typing are deterministic | UNREVIEWED | `REPLAN-FAILURE-001`; state and agent tests |
| Hidden evaluator data and scores cannot enter prompts, tools or observations | UNREVIEWED | binding architecture, frozen-instance leakage tests |
| Trajectories expose enough information to audit policy adherence and costs | UNREVIEWED | controller-discrimination dry-run record |
| Injected tests distinguish scientific self-checking from execution-error recovery | UNREVIEWED | `reviewing` vs `retrying/replanning` trajectory signatures |

Overall decision: `UNREVIEWED`  
Signature or verifiable approval record: `UNASSIGNED`
