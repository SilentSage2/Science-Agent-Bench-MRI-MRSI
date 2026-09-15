# Primary-study freeze signoff

Current decision: **NO-GO — UNSIGNED DEVELOPMENT PACKET**

The current mechanically generated candidate lock is
`protocol/candidate_freeze_v8.json`. It binds the reviewed implementation revision
and immutable executor digest but deliberately keeps `primary_run_authorized` set
to `false` until this signoff is complete.

Freeze identifiers:

| Artifact | Frozen value |
|---|---|
| Git revision | `2672de1ceb2b7fdbed2884bbbda91363f52e82f1` |
| Task-manifest SHA-256 | UNASSIGNED |
| Prompt/schema SHA-256 | UNASSIGNED |
| Grader SHA-256 | UNASSIGNED |
| Analysis SHA-256 | UNASSIGNED |
| Model/provider settings | UNASSIGNED |
| Hard budget and pricing basis | UNASSIGNED |
| Executor image digest | `sha256:fbb0cde9a40ec156133c67b434a719615f8b2bc3df7744e1087911a0bb950f1c` |

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
