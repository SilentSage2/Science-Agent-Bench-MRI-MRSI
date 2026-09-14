# Paired-validity design sensitivity v1

Status: **design calculation, not observed power or a research result**  
Date: 2026-09-14

The former 12-instance/72-run schedule was chosen from deadline convenience. This calculation asks how many independent paired instances would be required, under a normal approximation for paired binary outcomes, for two-sided α=0.05 and 80% power across plausible absolute effects and discordant-pair probabilities.

| Discordant probability | 10-point effect | 15-point effect | 20-point effect |
|---:|---:|---:|---:|
| 0.25 | 189 | 80 | 42 |
| 0.35 | 267 | 115 | 61 |
| 0.50 | 385 | 167 | 91 |

For the working middle scenario—20 percentage points absolute effect and 0.35 discordance—the approximation requires 61 independent paired instances. Repeated model calls and generator seeds do not automatically create independent scientific instances.

This falsifies the assumption that 12 instances are automatically adequate for a confirmatory binary-validity claim. Unless pilot data and a frozen model justify a different design, the ISMRM deadline scope must be descriptive/feasibility or use a continuous prespecified MR-validity metric with its own sensitivity analysis. The final analysis remains paired and task-family aware.

Reproduce with:

```bash
PYTHONPATH=src python3.12 -m science_agent.design_sensitivity
```
