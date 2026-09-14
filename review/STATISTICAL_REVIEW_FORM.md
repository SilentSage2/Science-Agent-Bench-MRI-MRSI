# Statistical and experimental-design review

Reviewer: `UNASSIGNED`  
Affiliation: `UNASSIGNED`  
Date: `UNASSIGNED`  
Source revision reviewed: `UNASSIGNED`

| Item | Decision | Evidence / issue |
|---|---|---|
| Independent task instance and clustering structure are correctly defined | UNREVIEWED | private manifest generator enforces 122 unique groups; repetitions pair within group |
| Sensitivity analysis justifies family-specific instances and repetitions | UNREVIEWED | `protocol/blinded_primary_design_v1.json`; 61/family proposal |
| Co-primary estimands and denominators are unambiguous | UNREVIEWED | protocol v1.1 and `paired_analysis.py` |
| Pairing and interval procedures match the dependence structure | UNREVIEWED | family-stratified instance-cluster bootstrap and exact sign-flip test implemented |
| Missing, provider-failed, budget-exhausted and policy-violating runs are handled prospectively | UNREVIEWED | design missingness section; analysis exclusion counts |
| Family/stratum pooling and heterogeneity summaries are prespecified | UNREVIEWED | families analyzed separately; no pooled headline effect |
| Multiplicity and interpretation of co-primary endpoints are prespecified | UNREVIEWED | **Open: alpha allocation/gatekeeping still requires reviewer decision** |
| Bootstrap/randomization seeds and software versions are frozen | UNREVIEWED | candidate lock and analysis CLI seed fields |
| Stopping, rerun and protocol-deviation rules prevent outcome-driven replacement | UNREVIEWED | protocol synopsis and missingness rules |
| Figure tables and independent number checks reproduce every submitted value | UNREVIEWED | Figure 3/4 JSON pipeline implemented; independent human check pending |

Critical issues: `NONE RECORDED`  
Major issues: `NONE RECORDED`  
Required sensitivity target and assumptions: `UNASSIGNED`

Overall decision: `UNREVIEWED`  
Signature or verifiable approval record: `UNASSIGNED`
