# MRSI spectral-axis evidence sheet

This sheet tells the spectroscopy reviewer exactly what to inspect. It is a
development-model description, not an approval of physical realism.

## Current encoded axis

| Property | Current value | Source |
|---|---:|---|
| Nucleus | synthetic proton (`1H`) | `task.json` metadata |
| Domain | frequency-domain complex spectra | generator and `spectra.npz` |
| Units | ppm | `spectra.npz: ppm` |
| Bounds | 0.5 to 5.0 ppm, inclusive | generator |
| Ordering | ascending in storage; plots should reverse the display axis by convention | generator / figure contract |
| Samples | 256 by default; minimum 128 | generator |
| Nominal field | 3.0 T development assumption | `task.json` metadata |
| Nominal proton frequency | 127.73243676 MHz | derived from 42.57747892 MHz/T × 3.0 T |
| Represented span | 4.5 ppm ≈ 574.796 Hz at the nominal field | derived metadata |
| Grid representation | inclusive frequency-domain sample grid, not an FFT-derived acquisition axis | `task.json` metadata |

The current simulator has no time-domain acquisition, dwell time, center
frequency/header transform, scanner convention, or vendor orientation. Those
quantities must not be inferred. If the claim requires raw-acquisition realism,
their absence is a **Major** issue and the generator must be extended before
freeze.

## Nominal components to inspect

| Component | Center | Development width parameter |
|---|---:|---:|
| Lipid-like nuisance | 1.30 ppm | 0.16 ppm |
| NAA-like | 2.02 ppm | 0.045 ppm |
| Glx-like | 2.35 ppm | 0.075 ppm |
| Creatine-like | 3.03 ppm | 0.040 ppm |
| Choline-like | 3.20 ppm | 0.048 ppm |
| Water-like nuisance | 4.70 ppm | 0.035 ppm |

These are deliberately simplified single-component shapes, not a full density-
matrix basis and not a claim of sequence-specific metabolite quantification.
The reviewer should decide whether that abstraction is adequate for the narrower
nuisance-removal claim.

## Reproducible checks

After materializing a frozen instance, the reviewer should check that metadata
and the array agree, that spacing is uniform, and that every public template has
the same axis:

```bash
PYTHONPATH=src python3.12 -m science_agent.frozen_instances \
  --manifest protocol/frozen_development_instances_v1.json \
  --output /tmp/sab-mrsi-axis-review

python3.12 - <<'PY'
import json
from pathlib import Path
import numpy as np

root = Path('/tmp/sab-mrsi-axis-review')
instance = next(path for path in root.iterdir() if path.name.startswith('mrsi-'))
task = json.loads((instance / 'inputs' / 'task.json').read_text())
with np.load(instance / 'inputs' / 'spectra.npz', allow_pickle=False) as data:
    ppm = data['ppm']
    print(task['spectral_axis'])
    print(ppm[0], ppm[-1], ppm.size, np.diff(ppm).min(), np.diff(ppm).max())
PY
```

The expert records acceptance or a linked issue in
`review/MRSI_REVIEW_FORM.md`. Any requested change to axis direction, field,
bandwidth, sampling representation, or component basis must be resolved before
the task/grader hashes are frozen.

