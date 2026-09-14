# OpenNeuro ds004068 metadata-only ingestion

Status: **real public header mapping smoke; not reconstruction validation**

The selected source is OpenNeuro dataset `ds004068`, immutable snapshot `1.0.3`
(`f10baa45d16affcea81d7006177d551410e1cd27`). Its BIDS
`dataset_description.json` declares CC0 and DOI
`10.18112/openneuro.ds004068.v1.0.3`. The dataset contains spinal-cord MRI from
48 participants; no data-use application is required for this public snapshot.

Only two public T2w JSON sidecars and the dataset description were read. No
NIfTI, DICOM, k-space, image pixels, participant table, or derived image was
downloaded or committed. Direct identifiers and operational scanner fields such
as acquisition time, institution address, station name, and device serial number
were excluded from the committed allowlisted header projections.

## Immutable source files

| Source path at tag 1.0.3 | SHA-256 of original public JSON |
|---|---|
| `dataset_description.json` | `3e659fcdd325671b08b41ccc85a6237e37b869d1937552c0bf001e7babb776cd` |
| `sub-ZS001/anat/sub-ZS001_T2w.json` | `ea347477ccf0012da94cf182d1db26a8b50bb205017d28f601ebb5792fee02a3` |
| `sub-ZS002/anat/sub-ZS002_T2w.json` | `c16642ebe6a63ca52071640a3a7ec57e99eb4ea6f6b0014aeddf280bbce8c035` |

The allowlisted projections retain real acquisition metadata: 3 T Siemens
Prisma_fit, 3D SE T2w, TE 0.12 s, TR 1.5 s, base resolution 320, in-plane
parallel reduction factor 3, pixel bandwidth 625 Hz, dwell time 2.5 μs, and
HeadNeck_64 receive-coil label.

Run the real metadata smoke:

```bash
PYTHONPATH=src python3.12 -m science_agent.public_ingestion \
  --registry protocol/public_sources_v1.json \
  --manifest protocol/openneuro_ds004068_header_manifest_v1.json \
  --data-root tests/fixtures/openneuro_ds004068
```

The two subject groups are intentionally assigned to different splits to prove
subject-level grouping. A mutation test reuses a subject across splits and must
fail. This source has image-domain BIDS metadata, not raw multi-coil k-space, so
it validates ingestion, field/acquisition mapping, and leakage controls only. It
cannot validate the MRI reconstruction endpoint or coil-sensitivity physics.

