# Independent review issue log

Use stable identifiers (`MRI-001`, `MRSI-001`, `STAT-001`, `CTRL-001`). Do not
delete closed issues; append verification evidence and the revision that resolved
them.

| ID | Severity | Opened by/date | Finding and evidence | Owner | Required resolution | Status | Verification/revision |
|---|---|---|---|---|---|---|---|
| CTRL-001 | Major | Internal pre-review / 2026-09-14 | Direct and reactive can use the same mechanics in the v4 development checkout. | UNASSIGNED | Define distinct prospective behavior and add trajectory-level discrimination tests. | Open | |
| CTRL-002 | Major | Internal pre-review / 2026-09-14 | Self-debug only retries typed failure and cannot revise a technically successful but scientifically dubious candidate. | UNASSIGNED | Add hidden-score-free scientific self-check and tests for successful-candidate revision. | Open | |
| STAT-001 | Major | Internal pre-review / 2026-09-14 | The 18-entry development manifest contains only six dependence groups and is not an independently sized confirmatory set. | UNASSIGNED | Freeze a blinded sensitivity analysis, independent primary manifest, and repetition plan. | Open | |

Severity definitions: **Critical** invalidates safety, isolation, leakage control, or
the central scientific claim; **Major** can change an endpoint, contrast, or MR
validity conclusion; **Minor** improves clarity or robustness without changing the
primary conclusion.

