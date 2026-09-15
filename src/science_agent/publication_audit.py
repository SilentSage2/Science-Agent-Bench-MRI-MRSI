"""Fail-closed audit of publication-facing development evidence boundaries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


class PublicationAuditError(ValueError):
    """Raised when publication-facing evidence is inconsistent or overstated."""


def audit_publication_evidence(root: Path) -> dict[str, Any]:
    """Verify structured evidence, figure provenance, and claim boundaries."""
    data_path = root / "experiments" / "baseline_figure_data_v1.json"
    renderer_path = root / "src" / "science_agent" / "development_figures.py"
    data = _json(data_path)
    if data.get("research_result") is not False or "no agent" not in str(data.get("scope")):
        raise PublicationAuditError("Figure 2 data must be explicit non-agent calibration")

    figure_root = root / "figures" / "development" / "artifacts"
    audited_figures: list[str] = []
    for name in ("figure_1_framework", "figure_2_task_calibration"):
        sidecar = _json(figure_root / f"{name}.json")
        if sidecar.get("research_result") is not False:
            raise PublicationAuditError(f"{name} must not be marked as a research result")
        if sidecar.get("agent_effect_claim_allowed") is not False:
            raise PublicationAuditError(f"{name} must prohibit agent-effect claims")
        if sidecar.get("source_data_sha256") != _sha256(data_path):
            raise PublicationAuditError(f"{name} data provenance mismatch")
        if sidecar.get("renderer_sha256") != _sha256(renderer_path):
            raise PublicationAuditError(f"{name} renderer provenance mismatch")
        exports = sidecar.get("exports")
        export_hashes = sidecar.get("export_sha256")
        if not isinstance(exports, dict) or not isinstance(export_hashes, dict):
            raise PublicationAuditError(f"{name} export provenance missing")
        for kind in ("svg", "png", "phone_preview"):
            export_path = figure_root / str(exports.get(kind))
            if not export_path.is_file() or export_hashes.get(kind) != _sha256(export_path):
                raise PublicationAuditError(f"{name} {kind} hash mismatch")
        qa = sidecar.get("qa", {})
        if not str(qa.get("visual_inspection", "")).startswith("PASSED-"):
            raise PublicationAuditError(f"{name} visual QA is not recorded")
        if qa.get("mr_domain_signoff") != "PENDING":
            raise PublicationAuditError(
                f"{name} development sidecar must retain pending MR signoff"
            )
        audited_figures.append(name)

    figure_two_text = (figure_root / "figure_2_task_calibration.svg").read_text(encoding="utf-8")
    for forbidden in ("10/10", "$0.049994", "24 model calls", "4/4 invalid"):
        if forbidden in figure_two_text:
            raise PublicationAuditError("Figure 2 contains development-controller outcome counts")

    openneuro_root = root / "tests" / "fixtures" / "openneuro_ds004068"
    evidence = _json(openneuro_root / "dataset_description.json")
    if evidence.get("License") != "CC0":
        raise PublicationAuditError("OpenNeuro license evidence is not CC0")
    sensitive = {"AcquisitionTime", "InstitutionAddress", "StationName", "DeviceSerialNumber"}
    for header in sorted(openneuro_root.glob("*.header.json")):
        unexpected = sensitive.intersection(_json(header))
        if unexpected:
            raise PublicationAuditError(
                f"sensitive OpenNeuro fields retained: {sorted(unexpected)}"
            )
    ingestion_doc = (root / "docs" / "OPENNEURO_DS004068_INGESTION.md").read_text(encoding="utf-8")
    if "cannot validate the MRI reconstruction endpoint" not in ingestion_doc:
        raise PublicationAuditError("OpenNeuro reconstruction-validity limitation missing")

    readme = (root / "README.md").read_text(encoding="utf-8")
    required_readme = (
        "paid 10-cell development checkout has run",
        "no signed, frozen primary real-model comparison has run",
    )
    if any(phrase not in readme for phrase in required_readme):
        raise PublicationAuditError("README development/primary boundary is inconsistent")

    draft = (root / "abstract" / "DRAFT.md").read_text(encoding="utf-8")
    if "NO REAL-MODEL PRIMARY RESULTS EXIST" not in draft:
        raise PublicationAuditError("abstract primary-results boundary missing")
    for forbidden in ("10/10", "$0.049994", "24 model calls"):
        if forbidden in draft:
            raise PublicationAuditError("development checkout numbers entered the abstract")

    signoff = (root / "review" / "SIGNOFF.md").read_text(encoding="utf-8")
    if "NO-GO" not in signoff or "UNREVIEWED" not in signoff:
        raise PublicationAuditError("review signoff must remain explicit NO-GO/UNREVIEWED")
    current_lock_path, current_lock = _latest_candidate_lock(root / "protocol")
    if current_lock.get("primary_run_authorized") is not False:
        raise PublicationAuditError("candidate lock unexpectedly authorizes the primary run")
    if current_lock_path.name not in signoff:
        raise PublicationAuditError("review signoff does not name the latest candidate lock")
    source_revision = current_lock.get("source_revision")
    if not isinstance(source_revision, str) or source_revision not in signoff:
        raise PublicationAuditError("review signoff does not bind the candidate source revision")

    return {
        "audit_schema": "publication-evidence-audit-v1",
        "status": "development-consistent-primary-no-go",
        "figures_verified": audited_figures,
        "figure_export_hashes_verified": 6,
        "openneuro_scope": "metadata-only-not-reconstruction-validity",
        "primary_run_authorized": False,
        "external_review_complete": False,
    }


def _latest_candidate_lock(protocol_root: Path) -> tuple[Path, dict[str, Any]]:
    locks = sorted(
        protocol_root.glob("candidate_freeze_v*.json"),
        key=lambda path: int(path.stem.rsplit("v", 1)[1]),
    )
    if not locks:
        raise PublicationAuditError("candidate lock missing")
    return locks[-1], _json(locks[-1])


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PublicationAuditError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    arguments = parser.parse_args()
    print(json.dumps(audit_publication_evidence(arguments.root), sort_keys=True))


if __name__ == "__main__":
    main()
