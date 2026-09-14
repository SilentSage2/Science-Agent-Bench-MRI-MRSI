"""Synthetic Cartesian MRI reconstruction task with hidden-reference grading."""

from __future__ import annotations

import cmath
import csv
import json
import math
import random
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from science_agent.grading import GradeReport

TASK_ID = "SAB-MRI-RECON-001"
_KSPACE_FIELDS = ("ky", "kx", "real", "imaginary", "sampled")
_IMAGE_FIELDS = ("y", "x", "value")
_RESULT_FIELDS = {
    "task_id",
    "method",
    "matrix_size",
    "reported_data_consistency_rmse",
    "conclusion_code",
}
_NUMERIC_TOLERANCE = 1e-8
_DATA_CONSISTENCY_LIMIT = 1e-8
_NRMSE_LIMIT = 0.9


class MRIReconstructionError(ValueError):
    """Raised when MRI task inputs or submitted artifacts are malformed."""


def create_mri_reconstruction_fixture(
    input_directory: Path,
    evaluator_directory: Path,
    *,
    seed: int,
    matrix_size: int = 16,
    acceleration: int = 4,
) -> None:
    """Create public undersampled k-space and an evaluator-only phantom."""
    if matrix_size < 8 or matrix_size % 2:
        raise MRIReconstructionError("matrix_size must be an even integer of at least 8")
    if acceleration < 2:
        raise MRIReconstructionError("acceleration must be at least 2")
    input_directory.mkdir(parents=True, exist_ok=False)
    evaluator_directory.mkdir(parents=True, exist_ok=False)
    image = _phantom(matrix_size, seed)
    full_kspace = _dft2(image, inverse=False)
    sampled_rows: list[dict[str, str]] = []
    for ky in range(matrix_size):
        frequency = min(ky, matrix_size - ky)
        sampled_line = frequency <= 1 or frequency % acceleration == 0
        for kx in range(matrix_size):
            value = full_kspace[ky][kx] if sampled_line else 0j
            sampled_rows.append(
                {
                    "ky": str(ky),
                    "kx": str(kx),
                    "real": f"{value.real:.17g}",
                    "imaginary": f"{value.imag:.17g}",
                    "sampled": "true" if sampled_line else "false",
                }
            )
    _write_csv(input_directory / "kspace.csv", _KSPACE_FIELDS, sampled_rows)
    task = {
        "task_id": TASK_ID,
        "schema_version": "1",
        "domain": "cartesian_mri_reconstruction",
        "matrix_size": matrix_size,
        "acceleration": acceleration,
        "objective": "reconstruct a real image while preserving sampled k-space",
        "required_artifacts": ["result.json", "reconstruction.csv"],
    }
    (input_directory / "task.json").write_text(
        json.dumps(task, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    reference_rows = [
        {"y": str(y), "x": str(x), "value": f"{image[y][x].real:.17g}"}
        for y in range(matrix_size)
        for x in range(matrix_size)
    ]
    _write_csv(evaluator_directory / "reference.csv", _IMAGE_FIELDS, reference_rows)
    (evaluator_directory / "metadata.json").write_text(
        json.dumps({"seed": seed, "generator_version": "phantom-v1"}, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def solve_mri_reconstruction_reference(input_directory: Path, output_directory: Path) -> None:
    """Produce a deterministic zero-filled inverse-DFT reconstruction."""
    matrix, sampled = _read_kspace(input_directory / "kspace.csv")
    reconstruction = _dft2(matrix, inverse=True)
    values = [[value.real for value in row] for row in reconstruction]
    consistency = _data_consistency_rmse(values, matrix, sampled)
    output_directory.mkdir(parents=True, exist_ok=False)
    result = {
        "task_id": TASK_ID,
        "method": "zero_filled_inverse_dft",
        "matrix_size": len(matrix),
        "reported_data_consistency_rmse": consistency,
        "conclusion_code": "reconstruction_complete",
    }
    (output_directory / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    rows = [
        {"y": str(y), "x": str(x), "value": f"{values[y][x]:.17g}"}
        for y in range(len(values))
        for x in range(len(values))
    ]
    _write_csv(output_directory / "reconstruction.csv", _IMAGE_FIELDS, rows)


def grade_mri_reconstruction(
    input_directory: Path,
    evaluator_directory: Path,
    output_directory: Path,
) -> GradeReport:
    try:
        result = _read_result(output_directory / "result.json")
        submitted = _read_image(output_directory / "reconstruction.csv")
        reference = _read_image(evaluator_directory / "reference.csv")
        kspace, sampled = _read_kspace(input_directory / "kspace.csv")
    except (OSError, json.JSONDecodeError, MRIReconstructionError, TypeError, ValueError) as exc:
        return GradeReport(False, False, False, False, (f"artifact_error:{exc}",))

    diagnostics: list[str] = []
    size = len(kspace)
    artifact_valid = result["task_id"] == TASK_ID and result["matrix_size"] == size
    if len(submitted) != size or any(len(row) != size for row in submitted):
        diagnostics.append("reconstruction_shape_mismatch")
        artifact_valid = False
    if len(reference) != size or any(len(row) != size for row in reference):
        return GradeReport(False, False, False, False, ("evaluator_reference_invalid",))
    if not artifact_valid:
        diagnostics.append("result_identity_or_size_mismatch")
        return GradeReport(False, False, False, False, tuple(diagnostics))

    consistency = _data_consistency_rmse(submitted, kspace, sampled)
    nrmse = _nrmse(reference, submitted)
    reported_consistency = result["reported_data_consistency_rmse"]
    numerical_correct = consistency <= _DATA_CONSISTENCY_LIMIT and math.isclose(
        reported_consistency,
        consistency,
        abs_tol=_NUMERIC_TOLERANCE,
        rel_tol=_NUMERIC_TOLERANCE,
    )
    if consistency > _DATA_CONSISTENCY_LIMIT:
        diagnostics.append("sampled_kspace_not_preserved")
    if not math.isclose(
        reported_consistency,
        consistency,
        abs_tol=_NUMERIC_TOLERANCE,
        rel_tol=_NUMERIC_TOLERANCE,
    ):
        diagnostics.append("reported_consistency_does_not_match")
    scientifically_valid = (
        numerical_correct
        and nrmse <= _NRMSE_LIMIT
        and result["conclusion_code"] == "reconstruction_complete"
    )
    if nrmse > _NRMSE_LIMIT:
        diagnostics.append("reconstruction_nrmse_above_limit")
    if result["conclusion_code"] != "reconstruction_complete":
        diagnostics.append("conclusion_not_supported")
    return GradeReport(
        artifact_valid,
        numerical_correct,
        scientifically_valid,
        artifact_valid and numerical_correct,
        tuple(diagnostics),
        {"data_consistency_rmse": consistency, "nrmse": nrmse},
    )


def _phantom(size: int, seed: int) -> list[list[complex]]:
    generator = random.Random(seed)
    offset_x = generator.uniform(-0.08, 0.08)
    offset_y = generator.uniform(-0.08, 0.08)
    image: list[list[complex]] = []
    for y in range(size):
        row: list[complex] = []
        normalized_y = 2.0 * y / (size - 1) - 1.0
        for x in range(size):
            normalized_x = 2.0 * x / (size - 1) - 1.0
            value = 0.0
            if ((normalized_x - offset_x) / 0.72) ** 2 + (
                (normalized_y - offset_y) / 0.88
            ) ** 2 <= 1.0:
                value += 0.8
            if ((normalized_x + 0.25) / 0.18) ** 2 + ((normalized_y - 0.2) / 0.25) ** 2 <= 1.0:
                value += 0.45
            if ((normalized_x - 0.28) / 0.12) ** 2 + ((normalized_y + 0.28) / 0.16) ** 2 <= 1.0:
                value -= 0.3
            row.append(complex(value, 0.0))
        image.append(row)
    return image


def _dft2(matrix: Sequence[Sequence[complex]], *, inverse: bool) -> list[list[complex]]:
    size = len(matrix)
    if not matrix or any(len(row) != size for row in matrix):
        raise MRIReconstructionError("DFT input must be a non-empty square matrix")
    sign = 1.0 if inverse else -1.0
    scale = 1.0 / (size * size) if inverse else 1.0
    output: list[list[complex]] = []
    for output_y in range(size):
        row: list[complex] = []
        for output_x in range(size):
            total = 0j
            for input_y in range(size):
                for input_x in range(size):
                    angle = (
                        sign
                        * 2.0
                        * math.pi
                        * (output_y * input_y / size + output_x * input_x / size)
                    )
                    total += matrix[input_y][input_x] * cmath.exp(1j * angle)
            row.append(total * scale)
        output.append(row)
    return output


def _data_consistency_rmse(
    image: Sequence[Sequence[float]],
    measured: Sequence[Sequence[complex]],
    sampled: Sequence[Sequence[bool]],
) -> float:
    predicted = _dft2([[complex(value) for value in row] for row in image], inverse=False)
    squared_errors = [
        abs(predicted[y][x] - measured[y][x]) ** 2
        for y in range(len(measured))
        for x in range(len(measured))
        if sampled[y][x]
    ]
    if not squared_errors:
        raise MRIReconstructionError("at least one k-space sample is required")
    return math.sqrt(sum(squared_errors) / len(squared_errors))


def _nrmse(reference: Sequence[Sequence[float]], actual: Sequence[Sequence[float]]) -> float:
    reference_values = [value for row in reference for value in row]
    actual_values = [value for row in actual for value in row]
    if len(reference_values) != len(actual_values) or not reference_values:
        raise MRIReconstructionError("NRMSE inputs must have equal non-zero size")
    numerator = math.sqrt(
        sum(
            (left - right) ** 2 for left, right in zip(reference_values, actual_values, strict=True)
        )
    )
    denominator = math.sqrt(sum(value**2 for value in reference_values))
    if denominator == 0.0:
        raise MRIReconstructionError("reference image must have non-zero energy")
    return numerator / denominator


def _read_kspace(path: Path) -> tuple[list[list[complex]], list[list[bool]]]:
    rows = _read_csv(path, _KSPACE_FIELDS)
    size = _infer_square_size(len(rows))
    matrix = [[0j for _ in range(size)] for _ in range(size)]
    sampled = [[False for _ in range(size)] for _ in range(size)]
    seen: set[tuple[int, int]] = set()
    for row in rows:
        ky = _bounded_index(row["ky"], size)
        kx = _bounded_index(row["kx"], size)
        if (ky, kx) in seen:
            raise MRIReconstructionError("duplicate k-space coordinate")
        seen.add((ky, kx))
        is_sampled = _boolean(row["sampled"])
        value = complex(_finite_float(row["real"]), _finite_float(row["imaginary"]))
        if not is_sampled and value != 0j:
            raise MRIReconstructionError("unsampled k-space entries must be zero")
        matrix[ky][kx] = value
        sampled[ky][kx] = is_sampled
    return matrix, sampled


def _read_image(path: Path) -> list[list[float]]:
    rows = _read_csv(path, _IMAGE_FIELDS)
    size = _infer_square_size(len(rows))
    image = [[0.0 for _ in range(size)] for _ in range(size)]
    seen: set[tuple[int, int]] = set()
    for row in rows:
        y = _bounded_index(row["y"], size)
        x = _bounded_index(row["x"], size)
        if (y, x) in seen:
            raise MRIReconstructionError("duplicate image coordinate")
        seen.add((y, x))
        image[y][x] = _finite_float(row["value"])
    return image


def _read_result(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) != _RESULT_FIELDS:
        raise MRIReconstructionError("result fields do not match schema")
    result = dict(value)
    matrix_size = value["matrix_size"]
    if isinstance(matrix_size, bool) or not isinstance(matrix_size, int) or matrix_size < 1:
        raise MRIReconstructionError("matrix_size must be a positive integer")
    result["reported_data_consistency_rmse"] = _finite_float(
        value["reported_data_consistency_rmse"]
    )
    for name in ("task_id", "method", "conclusion_code"):
        if not isinstance(value[name], str) or not value[name]:
            raise MRIReconstructionError(f"{name} must be a non-empty string")
    return result


def _read_csv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != fields:
            raise MRIReconstructionError(f"{path.name} columns do not match schema")
        rows = [dict(row) for row in reader]
    if not rows or any(value == "" for row in rows for value in row.values()):
        raise MRIReconstructionError(f"{path.name} must contain non-empty values")
    return rows


def _write_csv(path: Path, fields: tuple[str, ...], rows: Sequence[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _infer_square_size(count: int) -> int:
    size = math.isqrt(count)
    if size * size != count:
        raise MRIReconstructionError("matrix row count must be a perfect square")
    return size


def _bounded_index(value: str, size: int) -> int:
    index = int(value)
    if not 0 <= index < size:
        raise MRIReconstructionError("matrix index is out of bounds")
    return index


def _boolean(value: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise MRIReconstructionError("boolean fields must be true or false")


def _finite_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise MRIReconstructionError("value is not numeric")
    number = float(value)
    if not math.isfinite(number):
        raise MRIReconstructionError("numeric values must be finite")
    return number
