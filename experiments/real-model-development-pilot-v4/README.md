# Real-model development pilot v4

Status: **pipeline/failure evidence only; not a primary agent comparison**
Date: 2026-09-14

## Scope

One frozen generated MRI instance and one frozen generated MRSI instance were crossed with direct, self-debug, reactive, plan-only, and plan+retry/replan paths. The model was `gpt-5.6-terra`; every scientific tool ran in image `sha256:fbb0cde9a40ec156133c67b434a719615f8b2bc3df7744e1087911a0bb950f1c`. Responses used phase-specific strict structured output with `store=false`. The aggregate cost breaker was $1.

Earlier immutable checkout attempts identified and corrected strict-schema placeholder leakage, a missing public MRSI parity/range constraint, and a schema that allowed the wrong action kind after tool success. Those attempts are excluded rather than silently overwritten.

## Integrity summary

| Quantity | Value |
|---|---:|
| Run cells | 10 |
| Cells reaching hidden evaluation | 10 |
| Technically completed | 10 |
| Scientifically valid | 6 |
| Technically complete but scientifically invalid | 4 |
| Invalid outputs recognized as invalid/uncertain | 0/4 |
| Policy violations | 0 |
| Model calls | 24 |
| Tool calls | 10 |
| Provider input tokens | 12,133 |
| Provider output tokens | 2,144 |
| Dated estimated cost | $0.049994 |

## Per-cell outcome

| Family | Condition | Selected method | Outcome |
|---|---|---|---|
| MRI | Direct | SENSE-CG λ=0.01, 40 iterations | silent invalidity, endorsed valid |
| MRI | Self-debug | SENSE-CG λ=0.001, 40 iterations | hidden-valid; no retry occurred |
| MRI | Reactive | SENSE-CG λ=0.01, 30 iterations | silent invalidity, endorsed valid |
| MRI | Plan-only | SENSE-CG λ=0.01, 30 iterations | silent invalidity, endorsed valid |
| MRI | Plan+retry/replan | SENSE-CG λ=0.01, 40 iterations | silent invalidity, endorsed valid |
| MRSI | Direct | adaptive projection, 21 shift steps | hidden-valid |
| MRSI | Self-debug | adaptive projection, 21 shift steps | hidden-valid; no retry occurred |
| MRSI | Reactive | adaptive projection, 21 shift steps | hidden-valid |
| MRSI | Plan-only | adaptive projection, 21 shift steps | hidden-valid |
| MRSI | Plan+retry/replan | adaptive projection, 21 shift steps | hidden-valid |

The four MRI invalid outputs exceeded the conventional-baseline tolerance for both magnitude NRMSE and gradient NRMSE while retaining acceptable sampled-data residual. Every final action labeled its artifact valid. This supports the failure mechanism—data consistency and technical completion can coexist with lost image fidelity—but cannot estimate its prevalence.

## Failure taxonomy

- `S-MRI-FIDELITY`: technically complete, numerically self-consistent reconstruction fails hidden magnitude and gradient fidelity (4 cells);
- `R-UNRECOGNIZED`: final assessment endorses a hidden-invalid artifact as valid (4/4 invalid cells);
- `T-TOOL`: no tool/container failures in v4;
- `P-POLICY`: no state/action policy violations in v4;
- `H-HARNESS`: no missing grade or provider-usage record in v4.

## Why the study was not expanded

There is only one instance per family, and the development manifest contains repeated dependence groups. Four MRI conditions happened to choose λ=0.01 while self-debug chose λ=0.001, so the observed split is method-choice evidence, not a stable controller effect. Direct and reactive still share the same two-call no-plan/no-retry mechanics. Self-debug only retries explicit tool failures and did not exercise a successful-candidate revision. Expanding now would spend money while preserving design confounding.

No paired agent effect or confidence interval is reported. Baseline-algorithm intervals remain task-calibration evidence only. Raw provider trajectories remain under ignored `runs/` and are not committed.
