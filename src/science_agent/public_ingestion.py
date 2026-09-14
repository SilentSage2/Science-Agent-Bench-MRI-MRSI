"""Validate external MR metadata, integrity, mapping, and leakage-safe splits."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any


class PublicIngestionError(ValueError):
    """Raised when an external-data ingestion record is unsafe or ambiguous."""


def validate_public_ingestion(
    registry_path: Path,
    manifest_path: Path,
    data_root: Path,
    *,
    smoke_mode: bool = False,
) -> dict[str, Any]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = {item["source_id"]: item for item in registry["sources"]}
    records = manifest.get("records")
    if not isinstance(records, list) or not records:
        raise PublicIngestionError("records must be a non-empty list")
    split_memberships: dict[tuple[str, str], set[str]] = defaultdict(set)
    seen_acquisitions: set[tuple[str, str]] = set()
    family_counts: Counter[str] = Counter()
    for record in records:
        source_id = record.get("source_id")
        if source_id not in sources:
            raise PublicIngestionError(f"unregistered source: {source_id}")
        source = sources[source_id]
        if record.get("family") != source["family"]:
            raise PublicIngestionError("record family does not match source registry")
        if not smoke_mode and record.get("access_approved") is not True:
            raise PublicIngestionError("data access/license approval is required")
        if smoke_mode and record.get("synthetic_metadata_only") is not True:
            raise PublicIngestionError("smoke records must be synthetic metadata only")
        split = record.get("split")
        if split not in {"development", "validation", "test"}:
            raise PublicIngestionError("split must be development, validation, or test")
        relative = record.get("relative_path")
        if not isinstance(relative, str):
            raise PublicIngestionError("relative_path is required")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts:
            raise PublicIngestionError("relative_path must stay inside data_root")
        path = data_root / pure
        if not path.is_file() or _sha256(path) != record.get("sha256"):
            raise PublicIngestionError("file integrity check failed")
        metadata = record.get("metadata")
        if not isinstance(metadata, dict):
            raise PublicIngestionError("metadata must be an object")
        if path.suffix == ".json":
            file_metadata = json.loads(path.read_text(encoding="utf-8"))
            if file_metadata != metadata:
                raise PublicIngestionError("manifest metadata does not match projected header")
        missing = set(source["required_mapping"]).difference(metadata)
        if missing:
            raise PublicIngestionError(f"required mapping fields missing: {sorted(missing)}")
        allowed_mapping = source.get("allowed_mapping")
        if allowed_mapping is not None:
            unexpected = set(metadata).difference(allowed_mapping)
            if unexpected:
                raise PublicIngestionError(
                    f"metadata contains non-allowlisted fields: {sorted(unexpected)}"
                )
        acquisition_key = (source_id, str(record.get("acquisition_id")))
        if acquisition_key in seen_acquisitions:
            raise PublicIngestionError("acquisition IDs must be unique within source")
        seen_acquisitions.add(acquisition_key)
        for split_key in source["split_keys"]:
            value = record.get(split_key)
            if not isinstance(value, str) or not value:
                raise PublicIngestionError(f"split key missing: {split_key}")
            split_memberships[(source_id, f"{split_key}:{value}")].add(split)
        family_counts[str(record["family"])] += 1
    leaked = [key for key, splits in split_memberships.items() if len(splits) > 1]
    if leaked:
        raise PublicIngestionError("subject/exam/acquisition leakage across splits")
    return {
        "ingestion_schema": "public-mr-metadata-smoke-v1",
        "smoke_mode": smoke_mode,
        "record_count": len(records),
        "family_counts": dict(sorted(family_counts.items())),
        "source_ids": sorted({str(record["source_id"]) for record in records}),
        "integrity_verified": True,
        "split_leakage_detected": False,
        "data_released": False,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--smoke-mode", action="store_true")
    arguments = parser.parse_args()
    result = validate_public_ingestion(
        arguments.registry,
        arguments.manifest,
        arguments.data_root,
        smoke_mode=arguments.smoke_mode,
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
