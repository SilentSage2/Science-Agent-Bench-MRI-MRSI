from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from science_agent.publication_audit import PublicationAuditError, audit_publication_evidence

ROOT = Path(__file__).resolve().parents[1]


def test_repository_publication_evidence_is_consistent() -> None:
    result = audit_publication_evidence(ROOT)

    assert result["status"] == "development-consistent-primary-no-go"
    assert result["figure_export_hashes_verified"] == 6
    assert result["primary_run_authorized"] is False


def test_figure_hash_mutation_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        copied = Path(temporary) / "repo"
        _copy_audit_fixture(copied)
        target = copied / "figures" / "development" / "artifacts" / "figure_2_task_calibration.svg"
        target.write_text(
            target.read_text(encoding="utf-8") + "<!-- mutation -->", encoding="utf-8"
        )

        with pytest.raises(PublicationAuditError, match="hash mismatch"):
            audit_publication_evidence(copied)


def _copy_audit_fixture(destination: Path) -> None:
    import shutil

    paths = (
        "experiments/baseline_figure_data_v1.json",
        "src/science_agent/development_figures.py",
        "figures/development/artifacts",
        "tests/fixtures/openneuro_ds004068",
        "docs/OPENNEURO_DS004068_INGESTION.md",
        "README.md",
        "abstract/DRAFT.md",
        "review/SIGNOFF.md",
        "protocol/candidate_freeze_v6.json",
    )
    for relative in paths:
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            target.write_bytes(source.read_bytes())
