"""Validate and materialize frozen development MRI/MRSI instance manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from science_agent.research.mri_multicoil import create_multicoil_reconstruction_instance
from science_agent.research.mrsi_nuisance import create_complex_mrsi_instance
from science_agent.trajectory import sha256_file


class FrozenInstanceError(ValueError):
    """Raised when a frozen manifest is ambiguous or unsafe."""


def materialize_frozen_instances(manifest_path: Path, output_root: Path) -> dict[str, Any]:
    """Generate every declared instance and record public/private file hashes."""
    manifest = _read_manifest(manifest_path)
    output_root.mkdir(parents=True, exist_ok=False)
    materialized: list[dict[str, Any]] = []
    for spec in manifest["instances"]:
        instance_id = str(spec["instance_id"])
        root = output_root / instance_id
        inputs = root / "inputs"
        evaluator = root / "evaluator"
        if spec["family"] == "mri_multicoil":
            create_multicoil_reconstruction_instance(
                inputs,
                evaluator,
                seed=int(spec["seed"]),
                matrix_size=int(spec["matrix_size"]),
                coils=int(spec["coils"]),
                acceleration=float(spec["acceleration"]),
                relative_noise=float(spec["relative_noise"]),
            )
        else:
            create_complex_mrsi_instance(
                inputs,
                evaluator,
                seed=int(spec["seed"]),
                grid_size=int(spec["grid_size"]),
                spectral_points=int(spec["spectral_points"]),
                difficulty=str(spec["difficulty"]),
            )
        materialized.append(
            {
                "instance_id": instance_id,
                "family": spec["family"],
                "dependence_group": spec["dependence_group"],
                "public_hashes": _directory_hashes(inputs),
                "evaluator_hashes": _directory_hashes(evaluator),
            }
        )
    record = {
        "manifest_sha256": sha256_file(manifest_path),
        "purpose": manifest["purpose"],
        "scientific_unit_warning": manifest["scientific_unit_warning"],
        "instance_count": len(materialized),
        "instances": materialized,
    }
    (output_root / "materialization.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return record


def _read_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("manifest_version") != "1":
        raise FrozenInstanceError("manifest version is unsupported")
    instances = value.get("instances")
    if not isinstance(instances, list) or not instances:
        raise FrozenInstanceError("instances must be a non-empty list")
    identifiers: set[str] = set()
    for item in instances:
        if not isinstance(item, dict):
            raise FrozenInstanceError("instance specifications must be objects")
        identifier = item.get("instance_id")
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            raise FrozenInstanceError("instance IDs must be unique non-empty strings")
        identifiers.add(identifier)
        if item.get("family") not in {"mri_multicoil", "mrsi_nuisance"}:
            raise FrozenInstanceError("instance family is unsupported")
        if not isinstance(item.get("dependence_group"), str) or not item["dependence_group"]:
            raise FrozenInstanceError("dependence_group is required")
        if isinstance(item.get("seed"), bool) or not isinstance(item.get("seed"), int):
            raise FrozenInstanceError("integer generator seed is required")
    return value


def _directory_hashes(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): sha256_file(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    result = materialize_frozen_instances(arguments.manifest, arguments.output)
    print(json.dumps({key: value for key, value in result.items() if key != "instances"}))


if __name__ == "__main__":
    main()
