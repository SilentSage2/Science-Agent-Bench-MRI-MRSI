from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from science_agent.public_ingestion import PublicIngestionError, validate_public_ingestion

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "protocol" / "public_sources_v1.json"
FIXTURES = ROOT / "tests" / "fixtures" / "public_ingestion"


def _manifest() -> dict[str, object]:
    mri = FIXTURES / "mri-header-smoke.txt"
    mrsi = FIXTURES / "mrsi-header-smoke.txt"
    return {
        "records": [
            {
                "source_id": "nyu-fastmri",
                "family": "mri_multicoil",
                "subject_id": "synthetic-subject-mri",
                "exam_id": "synthetic-exam-mri",
                "acquisition_id": "synthetic-acq-mri",
                "split": "development",
                "relative_path": mri.name,
                "sha256": hashlib.sha256(mri.read_bytes()).hexdigest(),
                "access_approved": False,
                "synthetic_metadata_only": True,
                "metadata": {
                    "anatomy": "synthetic-knee",
                    "coil_count": 8,
                    "matrix_shape": [64, 64],
                    "acquisition": "synthetic-cartesian",
                    "field_strength_t": 3.0,
                },
            },
            {
                "source_id": "ismrm-mrs-fitting-challenge-2016",
                "family": "mrsi_nuisance",
                "subject_id": "synthetic-subject-mrsi",
                "acquisition_id": "synthetic-acq-mrsi",
                "split": "development",
                "relative_path": mrsi.name,
                "sha256": hashlib.sha256(mrsi.read_bytes()).hexdigest(),
                "access_approved": False,
                "synthetic_metadata_only": True,
                "metadata": {
                    "nucleus": "1H",
                    "field_strength_t": 3.0,
                    "spectral_points": 256,
                    "ppm_min": 0.5,
                    "ppm_max": 5.0,
                    "spectral_width_hz": 574.79596542,
                },
            },
        ]
    }


def _write_manifest(root: Path, payload: dict[str, object]) -> Path:
    path = root / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_metadata_only_ingestion_smoke_checks_mapping_integrity_and_splits() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        manifest = _write_manifest(Path(temporary), _manifest())
        result = validate_public_ingestion(REGISTRY, manifest, FIXTURES, smoke_mode=True)

    assert result["record_count"] == 2
    assert result["integrity_verified"] is True
    assert result["split_leakage_detected"] is False
    assert result["data_released"] is False


def test_real_ingestion_requires_access_approval() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        manifest = _write_manifest(Path(temporary), _manifest())
        with pytest.raises(PublicIngestionError, match="access/license"):
            validate_public_ingestion(REGISTRY, manifest, FIXTURES, smoke_mode=False)


def test_subject_leakage_across_splits_fails_closed() -> None:
    payload = _manifest()
    records = payload["records"]
    assert isinstance(records, list)
    duplicate = dict(records[0])
    duplicate["acquisition_id"] = "synthetic-acq-mri-two"
    duplicate["exam_id"] = "synthetic-exam-mri-two"
    duplicate["split"] = "test"
    records.append(duplicate)
    with tempfile.TemporaryDirectory() as temporary:
        manifest = _write_manifest(Path(temporary), payload)
        with pytest.raises(PublicIngestionError, match="leakage"):
            validate_public_ingestion(REGISTRY, manifest, FIXTURES, smoke_mode=True)


def test_path_traversal_is_rejected() -> None:
    payload = _manifest()
    records = payload["records"]
    assert isinstance(records, list)
    records[0]["relative_path"] = "../outside"
    with tempfile.TemporaryDirectory() as temporary:
        manifest = _write_manifest(Path(temporary), payload)
        with pytest.raises(PublicIngestionError, match="inside data_root"):
            validate_public_ingestion(REGISTRY, manifest, FIXTURES, smoke_mode=True)
