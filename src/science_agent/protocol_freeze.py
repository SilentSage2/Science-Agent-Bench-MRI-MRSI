"""Create an auditable candidate protocol lock without embedding secrets or run data."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

FREEZE_GROUPS: dict[str, tuple[str, ...]] = {
    "controller_prompt_schema": (
        "src/science_agent/agent.py",
        "src/science_agent/live_pilot.py",
        "src/science_agent/contracts.py",
        "protocol/controller_adversarial_fixtures_v1.json",
    ),
    "task_generators_and_graders": (
        "src/science_agent/research/mri_multicoil.py",
        "src/science_agent/research/mrsi_nuisance.py",
        "src/science_agent/research_task_tools.py",
        "src/science_agent/primary_manifest.py",
        "src/science_agent/frozen_instances.py",
        "protocol/primary_manifest_spec_v1.json",
    ),
    "protocol_and_analysis": (
        "protocol/five_condition_protocol_v1.json",
        "protocol/blinded_primary_design_v1.json",
        "protocol/figure_data_contract_v1.json",
        "protocol/public_sources_v1.json",
        "protocol/public_ingestion_smoke_manifest_v1.json",
        "src/science_agent/design_sensitivity.py",
        "src/science_agent/silent_invalidity.py",
        "src/science_agent/paired_analysis.py",
        "src/science_agent/public_ingestion.py",
    ),
    "executor": (
        "docker/research.Dockerfile",
        "src/science_agent/container_executor.py",
    ),
}


def create_candidate_freeze(
    root: Path,
    *,
    source_revision: str,
    requested_model: str,
    executor_image: str,
) -> dict[str, Any]:
    """Hash every declared input and record the model-alias reproducibility boundary."""
    if not source_revision.strip() or not requested_model.strip():
        raise ValueError("source_revision and requested_model must not be empty")
    if not _DIGEST.fullmatch(executor_image):
        raise ValueError("executor_image must be an immutable sha256 digest")
    groups: dict[str, dict[str, str]] = {}
    for group, paths in FREEZE_GROUPS.items():
        groups[group] = {}
        for relative in paths:
            path = root / relative
            if not path.is_file():
                raise FileNotFoundError(relative)
            groups[group][relative] = _sha256(path)
    return {
        "freeze_schema": "candidate-protocol-lock-v1",
        "status": "candidate-no-go-pending-expert-signoff",
        "source_revision": source_revision,
        "requested_model": requested_model,
        "model_identity": {
            "immutable_snapshot_available": False,
            "limitation": (
                "The provider exposes the requested model as an alias in this study. "
                "Every response-returned model string and response ID must be retained; "
                "cross-date reruns may still experience unobservable alias drift."
            ),
            "required_run_fields": ["requested_model", "returned_model", "response_id"],
        },
        "executor_image": executor_image,
        "file_sha256": groups,
        "primary_run_authorized": False,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    payload = create_candidate_freeze(
        arguments.root,
        source_revision=arguments.source_revision,
        requested_model=arguments.model,
        executor_image=arguments.image,
    )
    arguments.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
