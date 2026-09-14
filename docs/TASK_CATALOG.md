# A1 task catalog

All task families require `outputs/result.json`, reject unknown fields, and expose only read-only inputs. CSV artifacts require exact headers and row identities. Graders separately emit artifact-validity, numerical-correctness, scientific-validity, and reproducibility decisions; task success requires all four.

| Family | Required evidence | Deterministic scientific check |
|---|---|---|
| `SAB-FIT-001` | selected model, coefficients, train/test RMSE, residual diagnostics, test predictions | Submitted predictions reproduce coefficients and selected model has lower held-out error |
| `SAB-DECAY-001` | decay, interval, nuisance parameters, weighted RMSE, method and conclusion | Fit beats constant baseline; interval contains hidden parameter or correctly reports non-identifiability |
| `SAB-NUM-001` | estimates/errors by step count, observed order, selected estimate | Independent reference confirms error decrease and expected convergence order |
| `SAB-SPECTRUM-001` | method, baseline, prominence, ordered peak table | One-to-one hidden-peak matching passes precision and recall thresholds |
| `SAB-SIM-001` | descriptives, effect, interval, p-value, method, seed | Seeded independent recomputation matches and conclusion agrees with declared alternative |
| `SAB-LEAK-001` | verdict, violation classes, row IDs, earliest timestamps | Exact independently derived violations, including clean-fixture false-positive checks |
| `SAB-ODE-001` | parameters/errors for both models, status, prediction trajectories | Trajectories reproduce from bounded parameters and selection passes held-out margin |

Each family starts with two development and three held-out instances, for 35 instances total. Hidden parameters are evaluator-only. Frozen-task corrections create a new suite version rather than silently changing an existing comparison.

Required negative grader fixtures cover malformed records, unknown fields, missing or duplicate rows, wrong units, non-finite or out-of-tolerance values, inconsistent statistics, path traversal, oversized output, and unsupported conclusions. A lucky scalar answer without required evidence cannot pass scientific validity.

