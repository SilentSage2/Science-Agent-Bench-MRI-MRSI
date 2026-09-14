# Development Figure 1/2 QA record

QA date: 2026-09-14  
Source revision: `d7be957f3b28303190ed2c00b9b33d46fe7f4680`  
Overall status: **visual/export QA passed; independent MR-domain signoff pending**

## Checks completed

- Inspected both 1800 × 1100 PNGs at original resolution and both 480 × 293
  phone previews. No clipping, overlap, missing glyph, or unreadable primary label
  was observed.
- Confirmed PNG metadata reports approximately 300 dpi for both full exports.
- Confirmed SVG and PNG use the same four-stage Figure 1 information structure.
- Confirmed color is redundant with text labels and uses the documented
  colorblind-safe Okabe–Ito subset.
- Confirmed captions explicitly scope Figure 1 as implemented design and Figure 2
  as task calibration.
- Confirmed Figure 2 reads only `experiments/baseline_figure_data_v1.json`, whose
  `research_result` field is `false`; it shows nine generated cases per family
  and contains no v4 controller-condition count.
- Confirmed the header badges remain visible at phone width:
  `PRIMARY STUDY NO-GO` and `NO AGENT EFFECT`.

## Export hashes

| Export | SHA-256 |
|---|---|
| `figure_1_framework.svg` | `e6263d267badf86f0a025c620d34eec8b7d32fd7bcba24f85ac4d3e009157983` |
| `figure_1_framework.png` | `b8b1f628c1d60da9f5cb627413c766fa4d773f88d3156131a3ddad1ebf601a9b` |
| `figure_1_framework_phone.png` | `67873560b973885742dfc5184b367d7e680263afd08224118096ec6dfc8e844d` |
| `figure_2_task_calibration.svg` | `bfe7b717db7510aa42d4426673cfca9ba605dedbf4d1f9fa330c19ea446dd388` |
| `figure_2_task_calibration.png` | `da8630dff30fc9d6b28b6cbc77c54422f6e18c93728039b642ebe5b8b00ddd3f` |
| `figure_2_task_calibration_phone.png` | `1385a3811c6f5abb481c050d6eecb236cf929d899b30ccb0ab1b82c187ed9ae1` |

## Open gate

An independent MRI/MRSI reviewer must still check scientific terminology,
endpoint framing, and caption sufficiency. Visual QA is not MR-domain approval and
does not change the primary-study NO-GO status.
