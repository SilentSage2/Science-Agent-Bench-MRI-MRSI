# Abstract evidence and format contract

## Working format

Use the official ISMRM 2026 standard-abstract rules until the 2027 call is available:

| Element | Working limit | Content contract |
|---|---:|---|
| Title | 125 characters | Informative and neutral; no positive outcome before result freeze |
| Synopsis | 100 words total | Motivation, Goal(s), Approach, Results; plain language and no citations |
| Impact | 40 words | Standalone, plain language, and tied to demonstrated rather than hoped-for results |
| Main body | 750 words | Introduction, Methods, Results, Discussion, Conclusion; references excluded |
| Review figures | ≤5 | Caption ≤500 characters for each |
| Preview | 1 image | No caption; simple and legible at smartphone width |

The 2027 call and rendered ECHO preview must be rechecked before submission. A stricter 2027 rule supersedes this contract.

## Evidence states

- `IMPLEMENTED`: present in released code and covered by repository tests;
- `VALIDATED-INFRASTRUCTURE`: demonstrated by deterministic smoke/security checks but not a research finding;
- `PLANNED`: protocol or placeholder with no completed frozen evidence;
- `FROZEN-RESULT`: derived by the locked analysis command from the immutable primary run set and independently verified.

Only `FROZEN-RESULT` may supply a numeric Results statement, comparative outcome, empirical Impact claim, result table, or Figures 3–5. `IMPLEMENTED` and `VALIDATED-INFRASTRUCTURE` may describe Methods or Figure 1/2 with their limitations. `PLANNED` text must carry that literal status and cannot use completed-study verbs.

## Section contract

- **Title:** asks about effect/change rather than claiming improvement until the sign and interval are known.
- **Synopsis:** Motivation and Goal(s) are stable; Approach updates only at protocol freeze; Results is populated only from the primary analysis output. The four fields together remain understandable outside the agent/MRSI niche.
- **Impact:** stands alone and states who can act differently because of the observed result. Null or adverse results receive an honest impact statement; positive-impact bias is prohibited.
- **Introduction:** defines the MR research-validity problem and the falsifiable controller question without repeating the Synopsis.
- **Methods:** reports generated/public data provenance, evaluator-isolated split, sensitivity-justified instance and repetition counts, pinned model and software, direct/self-debug baselines, three paired controller conditions, conventional MR references, meaningful tools, Docker boundary, budgets, primary/secondary metrics, controlled ablations, uncertainty, missingness/exclusion rules, seeds, and reproduction command.
- **Results:** reports completed/eligible `n`, paired point estimates and 95% intervals, family-stratified effects, efficiency, policy violations, and failure/recovery analysis. It never converts a smoke test into model evidence.
- **Discussion:** explains magnitude and uncertainty, negative/null findings, task-family heterogeneity, failure modes, synthetic-data limitations, model/provider scope, small sample, and non-clinical scope.
- **Conclusion:** directly answers whether planning and bounded replan changed scientific validity under fixed budgets, using the observed sign and uncertainty.
- **References:** numbered in citation order and frozen after technical literature review; format instructions are not scientific references.

## Cross-artifact fact lock

`FACT_MAP.md` is the claim registry. At result freeze, one release commit must bind:

- primary run manifest and inclusion/exclusion ledger;
- `analysis/paired_outcomes.json`;
- `analysis/effect_estimates.json`;
- `analysis/efficiency.json`;
- `analysis/failure_index.json`;
- result table, abstract text, captions, figure sidecars, and README results section.

Each displayed number resolves to one fact ID and analysis key. Rounding may differ only according to a frozen display rule. Hand-entered values and post hoc rerun substitution are prohibited.

## Submission gate

The package is submission-ready only when the validator passes and all of the following are true:

1. 2027 rules are reconciled and recorded.
2. Protocol, held-out instances, model, tools, budgets, prompts, seeds, exclusions, and analysis are frozen before primary outcomes are opened.
3. The eligible primary run set is complete or missingness is explicitly analyzed.
4. Results, Synopsis Results, Impact, Conclusion, table, captions, figures, and README agree with the same fact map.
5. Statistical, MR-domain, independent-number, visual, and final-language reviews are signed.
6. No `PLANNED` token remains in a submitted field and no unsupported causal or clinical claim remains.
