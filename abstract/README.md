# ISMRM 2027 abstract package

This directory is the single submission-facing package for the MRI/MRSI agent-benchmark project. It uses the official 2026 standard-abstract format as a working template and must be checked against the 2027 call when it opens.

Current package status: **PLANNED / NOT SUBMISSION-READY**. No frozen real-model comparison exists, so the Results, final Impact, result-dependent captions, and conclusion remain explicitly planned. Infrastructure smoke results must not be substituted for scientific results.

Files:

- `ABSTRACT_CONTRACT.md`: format, evidence, freeze, and acceptance rules;
- `DRAFT.md`: title, structured synopsis, impact, main body, and references working draft;
- `FACT_MAP.md`: the allowed source of every claim across text, tables, captions, figures, and README;
- `CAPTIONS.md`: submission-facing caption drafts and preview-image rule.

Validate the current package with:

```bash
PYTHONPATH=src python3.12 -m science_agent.abstract_package abstract
```

The validator checks the 2026 working limits: title ≤125 characters, combined Synopsis ≤100 words, Impact ≤40 words, body ≤750 words, no more than five captions, and each caption ≤500 characters. It does not replace scientific, statistical, or 2027 submission-system review.

The final release gate is intentionally failing today:

```bash
PYTHONPATH=src python3.12 -m science_agent.abstract_package abstract --submission-ready
```

It rejects every unresolved `PLANNED` evidence placeholder. Passing length checks alone never means the abstract is scientifically ready.

Primary format sources:

- [2026 Standard Abstract Submission Guidelines](https://www.ismrm.org/26m/call/standard/)
- [2026 Impact & Synopsis Guide](https://www.ismrm.org/26m/call/submission-guide/impact-synopsis/)
- [2026 ECHO submission guide](https://www.ismrm.org/26m/call/submission-guide/)

Public proceedings inspected for common communication structure include [scanner-integrated qMRI](https://archive.ismrm.org/2025/0340.html), [virtual contrast MRI](https://archive.ismrm.org/2025/3241.html), and [low-field MRI reconstruction](https://archive.ismrm.org/2025/0343.html). They reinforce a concise broad-audience Motivation/Goal(s)/Approach/Results synopsis followed by a technically specific main report. They are structural examples, not evidence for this project.
