"""Generated MRI/MRSI split-leakage task and exact-set grader."""

from __future__ import annotations

import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from science_agent.grading import GradeReport

TASK_ID = "SAB-MRI-LEAK-001"
VIOLATION_CLASSES = (
    "future_feature",
    "subject_overlap",
    "target_derived_feature",
    "duplicate_across_split",
)
_RESULT_FIELDS = {
    "task_id",
    "audit_verdict",
    "violation_count_by_class",
    "affected_row_ids",
    "earliest_offending_timestamp",
    "conclusion_code",
}
_FEATURE_FIELDS = (
    "row_id",
    "subject_id",
    "event_time",
    "feature_available_time",
    "feature_name",
    "target_derived",
    "acquisition_hash",
)


class MRILeakageAuditError(ValueError):
    """Raised when MRI leakage data or a submitted artifact violates its schema."""


def create_mri_leakage_fixture(directory: Path, *, seed: int, include_violations: bool) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    generator = random.Random(seed)
    splits = ["train"] * 4 + ["validation"] * 3 + ["test"] * 3
    rows: list[dict[str, str]] = []
    for index, split in enumerate(splits):
        event_day = index + 1
        rows.append(
            {
                "row_id": f"row-{index:03d}",
                "subject_id": f"subject-{index:03d}",
                "event_time": f"2026-01-{event_day:02d}T00:00:00Z",
                "feature_available_time": f"2025-12-{min(31, event_day + 10):02d}T00:00:00Z",
                "feature_name": "reconstruction_quality_score",
                "target_derived": "false",
                "acquisition_hash": f"acq-{generator.randrange(10_000_000):07d}",
                "split": split,
            }
        )
    if include_violations:
        rows[5]["feature_available_time"] = "2026-02-01T00:00:00Z"
        rows[7]["subject_id"] = rows[1]["subject_id"]
        rows[8]["target_derived"] = "true"
        rows[9]["acquisition_hash"] = rows[2]["acquisition_hash"]

    with (directory / "features.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=_FEATURE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row[name] for name in _FEATURE_FIELDS})
    with (directory / "splits.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("row_id", "split"))
        writer.writeheader()
        for row in rows:
            writer.writerow({"row_id": row["row_id"], "split": row["split"]})
    metadata = {"task_id": TASK_ID, "schema_version": "1", "seed": seed}
    (directory / "task.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def solve_mri_leakage_reference(input_directory: Path, output_directory: Path) -> None:
    violations, timestamps = _derive_violations(input_directory)
    has_violations = any(violations.values())
    result = {
        "task_id": TASK_ID,
        "audit_verdict": "fail" if has_violations else "pass",
        "violation_count_by_class": {name: len(violations[name]) for name in VIOLATION_CLASSES},
        "affected_row_ids": {name: violations[name] for name in VIOLATION_CLASSES},
        "earliest_offending_timestamp": timestamps,
        "conclusion_code": "invalid_experiment" if has_violations else "valid_experiment",
    }
    output_directory.mkdir(parents=True, exist_ok=False)
    (output_directory / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def grade_mri_leakage(input_directory: Path, output_directory: Path) -> GradeReport:
    try:
        result = _read_result(output_directory / "result.json")
        expected, expected_timestamps = _derive_violations(input_directory)
    except (OSError, json.JSONDecodeError, MRILeakageAuditError, TypeError, ValueError) as exc:
        return GradeReport(False, False, False, False, (f"artifact_error:{exc}",))

    diagnostics: list[str] = []
    artifact_valid = result["task_id"] == TASK_ID
    if not artifact_valid:
        diagnostics.append("wrong_task_id")
    expected_counts = {name: len(expected[name]) for name in VIOLATION_CLASSES}
    numerical_correct = (
        result["violation_count_by_class"] == expected_counts
        and result["affected_row_ids"] == expected
        and result["earliest_offending_timestamp"] == expected_timestamps
    )
    if not numerical_correct:
        diagnostics.append("violation_sets_or_counts_do_not_match")
    has_violations = any(expected.values())
    scientifically_valid = result["audit_verdict"] == (
        "fail" if has_violations else "pass"
    ) and result["conclusion_code"] == (
        "invalid_experiment" if has_violations else "valid_experiment"
    )
    if not scientifically_valid:
        diagnostics.append("verdict_or_conclusion_not_supported")
    reproducible = artifact_valid and numerical_correct
    return GradeReport(
        artifact_valid,
        numerical_correct,
        scientifically_valid,
        reproducible,
        tuple(diagnostics),
    )


def _derive_violations(input_directory: Path) -> tuple[dict[str, list[str]], dict[str, str | None]]:
    features = _read_csv(input_directory / "features.csv", _FEATURE_FIELDS)
    split_rows = _read_csv(input_directory / "splits.csv", ("row_id", "split"))
    splits = {row["row_id"]: row["split"] for row in split_rows}
    if len(splits) != len(split_rows) or set(splits) != {row["row_id"] for row in features}:
        raise MRILeakageAuditError("split rows must map one-to-one to feature rows")

    violations: dict[str, set[str]] = {name: set() for name in VIOLATION_CLASSES}
    subject_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    hash_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in features:
        if row["feature_available_time"] > row["event_time"]:
            violations["future_feature"].add(row["row_id"])
        if row["target_derived"] == "true":
            violations["target_derived_feature"].add(row["row_id"])
        elif row["target_derived"] != "false":
            raise MRILeakageAuditError("target_derived must be true or false")
        subject_groups[row["subject_id"]].append(row)
        hash_groups[row["acquisition_hash"]].append(row)

    for rows in subject_groups.values():
        if len({splits[row["row_id"]] for row in rows}) > 1:
            violations["subject_overlap"].update(row["row_id"] for row in rows)
    for rows in hash_groups.values():
        if len({splits[row["row_id"]] for row in rows}) > 1:
            violations["duplicate_across_split"].update(row["row_id"] for row in rows)

    ordered = {name: sorted(violations[name]) for name in VIOLATION_CLASSES}
    timestamps: dict[str, str | None] = {}
    by_id = {row["row_id"]: row for row in features}
    for name in VIOLATION_CLASSES:
        timestamps[name] = min(
            (by_id[row_id]["event_time"] for row_id in ordered[name]), default=None
        )
    return ordered, timestamps


def _read_result(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) != _RESULT_FIELDS:
        raise MRILeakageAuditError("result fields do not match schema")
    for field_name in (
        "violation_count_by_class",
        "affected_row_ids",
        "earliest_offending_timestamp",
    ):
        field_value = value[field_name]
        if not isinstance(field_value, dict) or tuple(sorted(field_value)) != tuple(
            sorted(VIOLATION_CLASSES)
        ):
            raise MRILeakageAuditError(f"{field_name} keys do not match violation classes")
    counts = value["violation_count_by_class"]
    if any(
        isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in counts.values()
    ):
        raise MRILeakageAuditError("violation counts must be non-negative integers")
    affected = value["affected_row_ids"]
    if any(
        not isinstance(items, list)
        or not all(isinstance(item, str) for item in items)
        or items != sorted(set(items))
        for items in affected.values()
    ):
        raise MRILeakageAuditError("affected row IDs must be sorted unique string lists")
    timestamps = value["earliest_offending_timestamp"]
    if any(item is not None and not isinstance(item, str) for item in timestamps.values()):
        raise MRILeakageAuditError("offending timestamps must be strings or null")
    return dict(value)


def _read_csv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != fields:
            raise MRILeakageAuditError(f"{path.name} columns do not match schema")
        rows = [dict(row) for row in reader]
    if not rows or any(not value for row in rows for value in row.values()):
        raise MRILeakageAuditError(f"{path.name} must contain non-empty values")
    return rows
