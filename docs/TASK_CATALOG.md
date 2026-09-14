# A1 task catalog

All task families require `outputs/result.json`, reject unknown fields, and expose only read-only inputs. CSV artifacts require exact headers and row identities. Graders separately emit artifact-validity, numerical-correctness, scientific-validity, and reproducibility decisions; task success requires all four.

| Family | Required evidence | Deterministic scientific check |
|---|---|---|
| `SAB-MRS-FIT-001` | selected metabolite basis model, coefficients, fit/held-out RMSE, residual diagnostics, predicted spectrum | Submitted spectrum reproduces coefficients and the selected NAA/Cr model has lower held-out error |
| `SAB-MRSI-NUIS-001` | corrected spectra, water/lipid suppression metrics, retained-metabolite error | Independent masks verify nuisance reduction without unacceptable metabolite loss |
| `SAB-MRI-RECON-001` | reconstructed phantom, method/config, data-consistency residual, image metrics | Forward model confirms sampled k-space consistency and reference image metrics |
| `SAB-MRI-QC-001` | artifact labels, affected slices/regions, severity and evidence table | Exact/tolerance matching recovers seeded motion, ghosting, spike, or bias-field artifacts |
| `SAB-MRSI-QUANT-001` | metabolite maps, uncertainty, residual and failure masks | Hidden concentrations and corrupted-voxel masks verify quantitative error and calibration |
| `SAB-MRI-LEAK-001` | verdict, violation classes, acquisition IDs, earliest timestamps | Exact independently derived subject overlap, future-feature, target-derived, and duplicate violations |
| `SAB-DYNMR-001` | parameters/errors for two kinetic models, status, prediction curves | Curves reproduce from bounded parameters and selection passes held-out predictive margin |

Four families now have executable development generators and graders; three remain at contract stage. These are small correctness fixtures, not research-grade tasks. MRI reconstruction and MRSI nuisance removal are the first depth targets; the others remain secondary until they pass the same realism, baseline, adversarial, and domain-review gate. Held-out counts are selected by blinded sensitivity analysis rather than a fixed three-per-family rule. Hidden parameters are evaluator-only. Frozen-task corrections create a new suite version rather than silently changing an existing comparison.

Required negative grader fixtures cover malformed records, unknown fields, missing or duplicate rows, wrong units, non-finite or out-of-tolerance values, inconsistent statistics, path traversal, oversized output, and unsupported conclusions. A lucky scalar answer without required evidence cannot pass scientific validity.
