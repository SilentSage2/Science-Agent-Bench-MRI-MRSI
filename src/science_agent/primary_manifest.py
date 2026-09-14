"""Create a private, sensitivity-sized primary manifest and public commitment."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any


class PrimaryManifestError(ValueError):
    """Raised when a primary manifest would violate independence or blinding."""


def create_primary_manifest(design_path: Path, spec_path: Path, seed_key: bytes) -> dict[str, Any]:
    if len(seed_key) < 32:
        raise PrimaryManifestError("seed key must contain at least 32 bytes")
    design = json.loads(design_path.read_text(encoding="utf-8"))
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    count = int(design["design_assumptions"]["required_independent_instances_per_family"])
    allocation = design["difficulty_allocation_per_family"]
    difficulties = [
        difficulty
        for difficulty in ("easy", "moderate", "hard")
        for _ in range(int(allocation[difficulty]))
    ]
    if len(difficulties) != count:
        raise PrimaryManifestError("difficulty allocation does not match sensitivity count")
    instances: list[dict[str, Any]] = []
    seen_seeds: set[int] = set()
    for family in design["families"]:
        for index, difficulty in enumerate(difficulties, start=1):
            label = f"{family}/{index:03d}".encode()
            seed = int.from_bytes(hmac.digest(seed_key, label, "sha256")[:8], "big") & (2**63 - 1)
            if seed in seen_seeds:
                raise PrimaryManifestError("derived seeds must be unique")
            seen_seeds.add(seed)
            prefix = "MRI" if family == "mri_multicoil" else "MRSI"
            item: dict[str, Any] = {
                "instance_id": f"{prefix}-primary-{index:03d}",
                "family": family,
                "dependence_group": f"{prefix}-latent-{index:03d}",
                "seed": seed,
                "difficulty": difficulty,
            }
            if family == "mri_multicoil":
                item.update(spec["mri_defaults"])
                item.update(spec["mri_difficulty"][difficulty])
            elif family == "mrsi_nuisance":
                item.update(spec["mrsi_defaults"])
            else:
                raise PrimaryManifestError(f"unsupported family: {family}")
            instances.append(item)
    manifest = {
        "manifest_version": "1",
        "purpose": "private primary-study candidate; not authorized until signoff",
        "scientific_unit_warning": (
            "Each dependence_group is one independently generated latent task instance. "
            "Conditions and repetitions are paired and clustered within it."
        ),
        "design_version": design["design_version"],
        "primary_run_authorized": False,
        "instances": instances,
    }
    validate_primary_manifest(manifest, expected_per_family=count)
    return manifest


def validate_primary_manifest(manifest: dict[str, Any], *, expected_per_family: int) -> None:
    instances = manifest.get("instances")
    if not isinstance(instances, list):
        raise PrimaryManifestError("instances must be a list")
    expected_total = expected_per_family * 2
    if len(instances) != expected_total:
        raise PrimaryManifestError("manifest does not match sensitivity-sized total")
    identifiers = [item.get("instance_id") for item in instances]
    groups = [item.get("dependence_group") for item in instances]
    seeds = [item.get("seed") for item in instances]
    if len(set(identifiers)) != expected_total:
        raise PrimaryManifestError("instance IDs must be unique")
    if len(set(groups)) != expected_total:
        raise PrimaryManifestError("one instance per dependence group is required")
    if len(set(seeds)) != expected_total:
        raise PrimaryManifestError("generator seeds must be unique")
    for family in ("mri_multicoil", "mrsi_nuisance"):
        members = [item for item in instances if item.get("family") == family]
        if len(members) != expected_per_family:
            raise PrimaryManifestError("each family must meet its sensitivity count")


def manifest_commitment(manifest: dict[str, Any]) -> str:
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--seed-key-file", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--commitment-output", type=Path, required=True)
    arguments = parser.parse_args()
    manifest = create_primary_manifest(
        arguments.design,
        arguments.spec,
        arguments.seed_key_file.read_bytes(),
    )
    arguments.private_output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    commitment = {
        "manifest_sha256": manifest_commitment(manifest),
        "instance_count": len(manifest["instances"]),
        "primary_run_authorized": False,
    }
    arguments.commitment_output.write_text(
        json.dumps(commitment, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
