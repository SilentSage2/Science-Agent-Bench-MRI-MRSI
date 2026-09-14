# Controller-discrimination dry-run v1

Status: **implemented plumbing evidence; not a model or scientific result**

Protocol v1.1 was replayed with scripted actions across both research families.
All 10 condition-family cells reached hidden evaluation. The action/transition
signatures were:

| Condition | Model actions | Distinguishing transition |
|---|---|---|
| Direct | tool | validity precommitted; automatic finalization; no post-observation model call |
| Self-debug | tool → tool → final | `reviewing` after a successful public observation |
| Reactive | tool → final | post-observation assessment without revision |
| Plan-only | plan → tool → final | `planning` |
| Plan + retry/replan | plan → tool → plan → tool → final | `planning`, `retrying`, `replanning` after injected typed failure |

The self-debug first candidate was a technically successful naive MRI/MRSI
method, followed by a distinct conventional candidate. The runtime separately
rejects a missing direct precommit, an early self-debug final, an unchanged
self-debug candidate, and a missing structured replan. Hidden scores were not
used to choose the scripted revisions.

Reproduce with:

```bash
PYTHONPATH=src python3.12 -m science_agent.research_dry_run \
  --output runs/controller-discrimination-dry-run-v1 \
  --acknowledge-non-model
```

This dry-run proves that the controller interventions are mechanically
distinguishable. It does not show that any controller improves MR validity.

