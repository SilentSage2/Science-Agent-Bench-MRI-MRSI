# Independent review issue log

Use stable identifiers (`MRI-001`, `MRSI-001`, `STAT-001`, `CTRL-001`). Do not
delete closed issues; append verification evidence and the revision that resolved
them.

| ID | Severity | Opened by/date | Finding and evidence | Owner | Required resolution | Status | Verification/revision |
|---|---|---|---|---|---|---|---|
| CTRL-001 | Major | Internal pre-review / 2026-09-14 | Direct and reactive used the same mechanics in the v4 development checkout. | Repository maintainer | Direct now precommits validity and receives no post-observation model call; reactive assesses after the first successful observation. Verify with trajectory tests and external review. | Implemented; verification pending | `tests/test_agent.py`; protocol v1.1 |
| CTRL-002 | Major | Internal pre-review / 2026-09-14 | Self-debug only retried typed failure and could not revise a technically successful but scientifically dubious candidate. | Repository maintainer | Require one hidden-score-free, public-diagnostic-conditioned candidate revision and reject an early final. | Implemented; verification pending | `tests/test_agent.py`; protocol v1.1 |
| STAT-001 | Major | Internal pre-review / 2026-09-14 | The 18-entry development manifest contains only six dependence groups and is not an independently sized confirmatory set. | Repository maintainer | Freeze a blinded sensitivity analysis, independent primary manifest, and repetition plan. | Generator and analysis implemented; statistical verification pending | `protocol/blinded_primary_design_v1.json`; `primary_manifest.py`; `paired_analysis.py` |
| MRSI-001 | Major | Internal pre-review / 2026-09-14 | The frequency-domain simulator has no time-domain acquisition, dwell time, center-frequency/header transform, or vendor convention. | UNASSIGNED | MRSI expert must determine whether the abstraction supports the nuisance-removal claim or require an acquisition-model extension. | Open | `review/MRSI_SPECTRAL_AXIS_EVIDENCE.md` |

Severity definitions: **Critical** invalidates safety, isolation, leakage control, or
the central scientific claim; **Major** can change an endpoint, contrast, or MR
validity conclusion; **Minor** improves clarity or robustness without changing the
primary conclusion.
