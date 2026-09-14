"""Synthetic MRSI water/lipid nuisance-removal task and grader."""

from __future__ import annotations

import csv
import json
import math
import random
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from science_agent.grading import GradeReport

TASK_ID = "SAB-MRSI-NUIS-001"
_INPUT_FIELDS = (
    "voxel_id",
    "y",
    "x",
    "frequency_ppm",
    "observed_signal",
    "water_template",
    "lipid_template",
)
_REFERENCE_FIELDS = ("voxel_id", "frequency_ppm", "clean_signal")
_OUTPUT_FIELDS = ("voxel_id", "frequency_ppm", "corrected_signal")
_RESULT_FIELDS = {
    "task_id",
    "method",
    "voxel_count",
    "mean_water_suppression_db",
    "mean_lipid_suppression_db",
    "conclusion_code",
}
_WATER_SUPPRESSION_LIMIT_DB = 20.0
_LIPID_SUPPRESSION_LIMIT_DB = 20.0
_RETENTION_NRMSE_LIMIT = 0.2
_METRIC_TOLERANCE = 1e-7


class MRSINuisanceError(ValueError):
    """Raised when an MRSI nuisance task file violates its schema."""


def create_mrsi_nuisance_fixture(
    input_directory: Path,
    evaluator_directory: Path,
    *,
    seed: int,
    grid_size: int = 3,
    spectral_points: int = 48,
) -> None:
    """Create public contaminated spectra and evaluator-only clean spectra."""
    if grid_size < 2:
        raise MRSINuisanceError("grid_size must be at least 2")
    if spectral_points < 32:
        raise MRSINuisanceError("spectral_points must be at least 32")
    input_directory.mkdir(parents=True, exist_ok=False)
    evaluator_directory.mkdir(parents=True, exist_ok=False)
    generator = random.Random(seed)
    input_rows: list[dict[str, str]] = []
    reference_rows: list[dict[str, str]] = []
    for y in range(grid_size):
        for x in range(grid_size):
            voxel_id = f"voxel-{y:02d}-{x:02d}"
            naa_amplitude = 0.8 + 0.12 * y
            cr_amplitude = 0.65 + 0.1 * x
            water_amplitude = 3.5 + generator.uniform(-0.4, 0.4)
            lipid_amplitude = 2.0 + generator.uniform(-0.3, 0.3)
            for index in range(spectral_points):
                frequency = 0.5 + 4.5 * index / (spectral_points - 1)
                naa = _gaussian(frequency, 2.02, 0.09)
                creatine = _gaussian(frequency, 3.03, 0.08)
                water = _gaussian(frequency, 4.7, 0.055)
                lipid = _gaussian(frequency, 1.3, 0.2)
                clean = (
                    0.015
                    + naa_amplitude * naa
                    + cr_amplitude * creatine
                    + generator.gauss(0.0, 0.003)
                )
                observed = clean + water_amplitude * water + lipid_amplitude * lipid
                input_rows.append(
                    {
                        "voxel_id": voxel_id,
                        "y": str(y),
                        "x": str(x),
                        "frequency_ppm": f"{frequency:.17g}",
                        "observed_signal": f"{observed:.17g}",
                        "water_template": f"{water:.17g}",
                        "lipid_template": f"{lipid:.17g}",
                    }
                )
                reference_rows.append(
                    {
                        "voxel_id": voxel_id,
                        "frequency_ppm": f"{frequency:.17g}",
                        "clean_signal": f"{clean:.17g}",
                    }
                )
    _write_csv(input_directory / "contaminated_spectra.csv", _INPUT_FIELDS, input_rows)
    _write_csv(
        evaluator_directory / "clean_reference.csv",
        _REFERENCE_FIELDS,
        reference_rows,
    )
    task = {
        "task_id": TASK_ID,
        "schema_version": "1",
        "domain": "proton_mr_spectroscopic_imaging",
        "objective": "remove water and lipid nuisance while retaining metabolite signal",
        "grid_size": grid_size,
        "spectral_points": spectral_points,
        "required_artifacts": ["result.json", "corrected_spectra.csv"],
    }
    (input_directory / "task.json").write_text(
        json.dumps(task, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (evaluator_directory / "metadata.json").write_text(
        json.dumps({"seed": seed, "generator_version": "mrsi-nuisance-v1"}, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def solve_mrsi_nuisance_reference(input_directory: Path, output_directory: Path) -> None:
    rows = _read_csv(input_directory / "contaminated_spectra.csv", _INPUT_FIELDS)
    grouped = _group_rows(rows)
    corrected_by_voxel: dict[str, list[float]] = {}
    for voxel_id, voxel_rows in grouped.items():
        observed = [_finite_float(row["observed_signal"]) for row in voxel_rows]
        water = [_finite_float(row["water_template"]) for row in voxel_rows]
        lipid = [_finite_float(row["lipid_template"]) for row in voxel_rows]
        water_coefficient, lipid_coefficient = _fit_templates(observed, water, lipid)
        corrected_by_voxel[voxel_id] = [
            signal - water_coefficient * water_value - lipid_coefficient * lipid_value
            for signal, water_value, lipid_value in zip(observed, water, lipid, strict=True)
        ]

    output_directory.mkdir(parents=True, exist_ok=False)
    output_rows: list[dict[str, str]] = []
    for voxel_id, voxel_rows in grouped.items():
        for row, corrected in zip(voxel_rows, corrected_by_voxel[voxel_id], strict=True):
            output_rows.append(
                {
                    "voxel_id": voxel_id,
                    "frequency_ppm": row["frequency_ppm"],
                    "corrected_signal": f"{corrected:.17g}",
                }
            )
    _write_csv(output_directory / "corrected_spectra.csv", _OUTPUT_FIELDS, output_rows)
    water_score, lipid_score = _public_suppression_metrics(input_directory, output_directory)
    result = {
        "task_id": TASK_ID,
        "method": "joint_template_projection",
        "voxel_count": len(grouped),
        "mean_water_suppression_db": water_score,
        "mean_lipid_suppression_db": lipid_score,
        "conclusion_code": "nuisance_removal_complete",
    }
    (output_directory / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def grade_mrsi_nuisance(
    input_directory: Path,
    evaluator_directory: Path,
    output_directory: Path,
) -> GradeReport:
    try:
        result = _read_result(output_directory / "result.json")
        metrics, failed = _evaluate_spectra(input_directory, evaluator_directory, output_directory)
    except (OSError, json.JSONDecodeError, MRSINuisanceError, TypeError, ValueError) as exc:
        return GradeReport(False, False, False, False, (f"artifact_error:{exc}",))

    diagnostics: list[str] = []
    artifact_valid = result["task_id"] == TASK_ID
    if not artifact_valid:
        diagnostics.append("wrong_task_id")
    expected_voxel_count = len(
        _group_rows(_read_csv(input_directory / "contaminated_spectra.csv", _INPUT_FIELDS))
    )
    if result["voxel_count"] != expected_voxel_count:
        artifact_valid = False
        diagnostics.append("voxel_count_does_not_match")

    numerical_correct = True
    for name in ("mean_water_suppression_db", "mean_lipid_suppression_db"):
        expected = metrics[name]
        if not math.isclose(
            result[name], expected, abs_tol=_METRIC_TOLERANCE, rel_tol=_METRIC_TOLERANCE
        ):
            numerical_correct = False
            diagnostics.append(f"incorrect_{name}")
    expected_conclusion = (
        "nuisance_removal_complete" if not failed else "nuisance_removal_incomplete"
    )
    scientifically_valid = not failed and result["conclusion_code"] == expected_conclusion
    if failed:
        diagnostics.append("one_or_more_voxels_failed_thresholds")
    if result["conclusion_code"] != expected_conclusion:
        diagnostics.append("conclusion_not_supported")
    return GradeReport(
        artifact_valid,
        numerical_correct,
        scientifically_valid,
        artifact_valid and numerical_correct,
        tuple(diagnostics),
        metrics,
    )


def _evaluate_spectra(
    input_directory: Path,
    evaluator_directory: Path,
    output_directory: Path,
) -> tuple[dict[str, float], list[str]]:
    inputs = _group_rows(_read_csv(input_directory / "contaminated_spectra.csv", _INPUT_FIELDS))
    references = _group_rows(
        _read_csv(evaluator_directory / "clean_reference.csv", _REFERENCE_FIELDS)
    )
    outputs = _group_rows(_read_csv(output_directory / "corrected_spectra.csv", _OUTPUT_FIELDS))
    if inputs.keys() != references.keys() or inputs.keys() != outputs.keys():
        raise MRSINuisanceError("voxel IDs do not match")
    water_scores: list[float] = []
    lipid_scores: list[float] = []
    retention_scores: list[float] = []
    failed: list[str] = []
    for voxel_id in inputs:
        input_rows = inputs[voxel_id]
        reference_rows = references[voxel_id]
        output_rows = outputs[voxel_id]
        input_frequencies = [row["frequency_ppm"] for row in input_rows]
        if input_frequencies != [
            row["frequency_ppm"] for row in reference_rows
        ] or input_frequencies != [row["frequency_ppm"] for row in output_rows]:
            raise MRSINuisanceError("frequency grids do not match")
        observed = [_finite_float(row["observed_signal"]) for row in input_rows]
        corrected = [_finite_float(row["corrected_signal"]) for row in output_rows]
        clean = [_finite_float(row["clean_signal"]) for row in reference_rows]
        water = [_finite_float(row["water_template"]) for row in input_rows]
        lipid = [_finite_float(row["lipid_template"]) for row in input_rows]
        water_score = _suppression_db(observed, corrected, water)
        lipid_score = _suppression_db(observed, corrected, lipid)
        retention_score = _nrmse(clean, corrected)
        water_scores.append(water_score)
        lipid_scores.append(lipid_score)
        retention_scores.append(retention_score)
        if (
            water_score < _WATER_SUPPRESSION_LIMIT_DB
            or lipid_score < _LIPID_SUPPRESSION_LIMIT_DB
            or retention_score > _RETENTION_NRMSE_LIMIT
        ):
            failed.append(voxel_id)
    metrics = {
        "mean_water_suppression_db": sum(water_scores) / len(water_scores),
        "mean_lipid_suppression_db": sum(lipid_scores) / len(lipid_scores),
        "mean_metabolite_retention_nrmse": sum(retention_scores) / len(retention_scores),
    }
    return metrics, sorted(failed)


def _public_suppression_metrics(
    input_directory: Path, output_directory: Path
) -> tuple[float, float]:
    inputs = _group_rows(_read_csv(input_directory / "contaminated_spectra.csv", _INPUT_FIELDS))
    outputs = _group_rows(_read_csv(output_directory / "corrected_spectra.csv", _OUTPUT_FIELDS))
    if inputs.keys() != outputs.keys():
        raise MRSINuisanceError("voxel IDs do not match")
    water_scores: list[float] = []
    lipid_scores: list[float] = []
    for voxel_id, input_rows in inputs.items():
        output_rows = outputs[voxel_id]
        if [row["frequency_ppm"] for row in input_rows] != [
            row["frequency_ppm"] for row in output_rows
        ]:
            raise MRSINuisanceError("frequency grids do not match")
        observed = [_finite_float(row["observed_signal"]) for row in input_rows]
        corrected = [_finite_float(row["corrected_signal"]) for row in output_rows]
        water = [_finite_float(row["water_template"]) for row in input_rows]
        lipid = [_finite_float(row["lipid_template"]) for row in input_rows]
        water_scores.append(_suppression_db(observed, corrected, water))
        lipid_scores.append(_suppression_db(observed, corrected, lipid))
    return (
        sum(water_scores) / len(water_scores),
        sum(lipid_scores) / len(lipid_scores),
    )


def _fit_templates(
    observed: Sequence[float], water: Sequence[float], lipid: Sequence[float]
) -> tuple[float, float]:
    if not observed or len(observed) != len(water) or len(observed) != len(lipid):
        raise MRSINuisanceError("template fit inputs must have equal non-zero length")
    observed_centered = _center(observed)
    water_centered = _center(water)
    lipid_centered = _center(lipid)
    water_water = _dot(water_centered, water_centered)
    lipid_lipid = _dot(lipid_centered, lipid_centered)
    water_lipid = _dot(water_centered, lipid_centered)
    determinant = water_water * lipid_lipid - water_lipid**2
    if abs(determinant) < 1e-12:
        raise MRSINuisanceError("nuisance templates are singular")
    water_observed = _dot(water_centered, observed_centered)
    lipid_observed = _dot(lipid_centered, observed_centered)
    water_coefficient = (water_observed * lipid_lipid - lipid_observed * water_lipid) / determinant
    lipid_coefficient = (lipid_observed * water_water - water_observed * water_lipid) / determinant
    return water_coefficient, lipid_coefficient


def _suppression_db(
    before: Sequence[float], after: Sequence[float], template: Sequence[float]
) -> float:
    centered_template = _center(template)
    denominator = _dot(centered_template, centered_template)
    if denominator == 0.0:
        raise MRSINuisanceError("nuisance template must have non-zero energy")
    before_coefficient = abs(_dot(_center(before), centered_template) / denominator)
    after_coefficient = abs(_dot(_center(after), centered_template) / denominator)
    epsilon = 1e-12
    return 20.0 * math.log10((before_coefficient + epsilon) / (after_coefficient + epsilon))


def _nrmse(reference: Sequence[float], actual: Sequence[float]) -> float:
    if not reference or len(reference) != len(actual):
        raise MRSINuisanceError("NRMSE inputs must have equal non-zero length")
    numerator = math.sqrt(
        sum((left - right) ** 2 for left, right in zip(reference, actual, strict=True))
    )
    denominator = math.sqrt(sum(value**2 for value in reference))
    if denominator == 0.0:
        raise MRSINuisanceError("reference spectrum must have non-zero energy")
    return numerator / denominator


def _center(values: Sequence[float]) -> list[float]:
    mean = sum(values) / len(values)
    return [value - mean for value in values]


def _dot(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(left, right, strict=True))


def _gaussian(value: float, center: float, width: float) -> float:
    return math.exp(-0.5 * ((value - center) / width) ** 2)


def _group_rows(rows: Sequence[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["voxel_id"]].append(row)
    return dict(grouped)


def _read_result(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) != _RESULT_FIELDS:
        raise MRSINuisanceError("result fields do not match schema")
    result = dict(value)
    voxel_count = value["voxel_count"]
    if isinstance(voxel_count, bool) or not isinstance(voxel_count, int) or voxel_count < 1:
        raise MRSINuisanceError("voxel_count must be a positive integer")
    for name in (
        "mean_water_suppression_db",
        "mean_lipid_suppression_db",
    ):
        result[name] = _finite_float(value[name])
    for name in ("task_id", "method", "conclusion_code"):
        if not isinstance(value[name], str) or not value[name]:
            raise MRSINuisanceError(f"{name} must be a non-empty string")
    return result


def _read_csv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != fields:
            raise MRSINuisanceError(f"{path.name} columns do not match schema")
        rows = [dict(row) for row in reader]
    if not rows or any(value == "" for row in rows for value in row.values()):
        raise MRSINuisanceError(f"{path.name} must contain non-empty values")
    return rows


def _write_csv(path: Path, fields: tuple[str, ...], rows: Sequence[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _finite_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise MRSINuisanceError("value is not numeric")
    number = float(value)
    if not math.isfinite(number):
        raise MRSINuisanceError("numeric values must be finite")
    return number
