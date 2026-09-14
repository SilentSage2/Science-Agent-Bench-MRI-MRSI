# Primary-study freeze signoff

Current decision: **NO-GO — UNSIGNED DEVELOPMENT PACKET**

The current mechanically generated candidate lock is
`protocol/candidate_freeze_v3.json`. It binds the reviewed implementation revision
and immutable executor digest but deliberately keeps `primary_run_authorized` set
to `false` until this signoff is complete.

Freeze identifiers:

| Artifact | Frozen value |
|---|---|
| Git revision | UNASSIGNED |
| Task-manifest SHA-256 | UNASSIGNED |
| Prompt/schema SHA-256 | UNASSIGNED |
| Grader SHA-256 | UNASSIGNED |
| Analysis SHA-256 | UNASSIGNED |
| Model/provider settings | UNASSIGNED |
| Hard budget and pricing basis | UNASSIGNED |
| Executor image digest | UNASSIGNED |

Required approvals:

| Role | Reviewer | Decision | Date | Signature / verifiable record |
|---|---|---|---|---|
| MRI reconstruction expert | UNASSIGNED | UNREVIEWED | UNASSIGNED | UNASSIGNED |
| MRS/MRSI expert | UNASSIGNED | UNREVIEWED | UNASSIGNED | UNASSIGNED |
| Statistician/methodologist | UNASSIGNED | UNREVIEWED | UNASSIGNED | UNASSIGNED |
| Agent/evaluation reviewer (recommended) | UNASSIGNED | UNREVIEWED | UNASSIGNED | UNASSIGNED |

Conflict declarations: `UNASSIGNED`

The study may change to **GO** only when the decision rule in `review/README.md`
is satisfied and a versioned commit replaces every required placeholder. Signing
acknowledges protocol validity within the reviewer's stated expertise; it does not
certify clinical use or guarantee a positive result.
