"""Synthetic MRS basis-model selection task and deterministic grader."""

from __future__ import annotations

import csv
import json
import math
import random
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from science_agent.grading import GradeReport

TASK_ID = "SAB-MRS-FIT-001"
_RESULT_FIELDS = {
    "task_id",
    "selected_model",
    "coefficients",
    "train_rmse",
    "test_rmse",
    "residual_mean",
    "residual_target_correlation",
    "prediction_row_count",
    "conclusion_code",
}
_PREDICTION_FIELDS = ("point_id", "predicted_signal")
_ABS_TOLERANCE = 1e-8


class MRSSpectralFitError(ValueError):
    """Raised when an MRS fixture or submitted artifact is malformed."""


def create_mrs_fit_fixture(directory: Path, *, seed: int, train_size: int = 24) -> None:
    """Create repeated noisy spectra where the NAA+Cr basis model should win."""
    if train_size < 8:
        raise MRSSpectralFitError("train_size must be at least 8")
    directory.mkdir(parents=True, exist_ok=False)
    generator = random.Random(seed)
    _write_rows(directory / "train.csv", generator, "train", train_size)
    _write_rows(directory / "test.csv", generator, "test", max(8, train_size // 3))
    metadata = {
        "task_id": TASK_ID,
        "schema_version": "1",
        "seed": seed,
        "domain": "proton_mr_spectroscopy",
        "objective": "select an NAA-only or NAA-plus-creatine basis model",
        "candidate_models": {
            "naa_only": ["intercept", "naa_basis"],
            "naa_and_cr": ["intercept", "naa_basis", "cr_basis"],
        },
        "selection_rule": "lowest_test_rmse",
        "units": {"frequency": "ppm", "signal": "a.u."},
    }
    (directory / "task.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def solve_mrs_fit_reference(input_directory: Path, output_directory: Path) -> None:
    """Produce a known-good artifact. The grader still recomputes every statistic."""
    train = _read_dataset(input_directory / "train.csv")
    test = _read_dataset(input_directory / "test.csv")
    candidates: dict[str, tuple[str, ...]] = {
        "naa_only": ("intercept", "naa_basis"),
        "naa_and_cr": ("intercept", "naa_basis", "cr_basis"),
    }
    fitted = {model_id: _fit(train, terms) for model_id, terms in candidates.items()}
    errors = {
        model_id: _rmse(_targets(test), _predict(test, coefficients))
        for model_id, coefficients in fitted.items()
    }
    selected = min(errors, key=errors.__getitem__)
    coefficients = fitted[selected]
    train_predictions = _predict(train, coefficients)
    test_predictions = _predict(test, coefficients)
    residuals = [
        target - prediction
        for target, prediction in zip(_targets(train), train_predictions, strict=True)
    ]
    result = {
        "task_id": TASK_ID,
        "selected_model": selected,
        "coefficients": coefficients,
        "train_rmse": _rmse(_targets(train), train_predictions),
        "test_rmse": _rmse(_targets(test), test_predictions),
        "residual_mean": sum(residuals) / len(residuals),
        "residual_target_correlation": _correlation(residuals, _targets(train)),
        "prediction_row_count": len(test),
        "conclusion_code": "naa_and_cr_preferred"
        if selected == "naa_and_cr"
        else "naa_only_preferred",
    }
    output_directory.mkdir(parents=True, exist_ok=False)
    (output_directory / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (output_directory / "predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=_PREDICTION_FIELDS)
        writer.writeheader()
        for row, prediction in zip(test, test_predictions, strict=True):
            writer.writerow(
                {
                    "point_id": row["point_id"],
                    "predicted_signal": f"{prediction:.17g}",
                }
            )


def grade_mrs_fit(input_directory: Path, output_directory: Path) -> GradeReport:
    diagnostics: list[str] = []
    try:
        result = _read_result(output_directory / "result.json")
        submitted_predictions = _read_predictions(output_directory / "predictions.csv")
        train = _read_dataset(input_directory / "train.csv")
        test = _read_dataset(input_directory / "test.csv")
    except (OSError, json.JSONDecodeError, MRSSpectralFitError, TypeError, ValueError) as exc:
        return GradeReport(False, False, False, False, (f"artifact_error:{exc}",))

    artifact_valid = True
    if result["task_id"] != TASK_ID:
        diagnostics.append("wrong_task_id")
        artifact_valid = False
    expected_ids = [str(row["point_id"]) for row in test]
    if list(submitted_predictions) != expected_ids:
        diagnostics.append("prediction_row_ids_do_not_match")
        artifact_valid = False
    if result["prediction_row_count"] != len(test):
        diagnostics.append("prediction_row_count_does_not_match")
        artifact_valid = False

    model_terms = {
        "naa_only": ("intercept", "naa_basis"),
        "naa_and_cr": ("intercept", "naa_basis", "cr_basis"),
    }
    selected = result["selected_model"]
    if selected not in model_terms:
        diagnostics.append("unknown_selected_model")
        return GradeReport(artifact_valid, False, False, False, tuple(diagnostics))
    coefficients = result["coefficients"]
    if set(coefficients) != set(model_terms[selected]):
        diagnostics.append("coefficient_terms_do_not_match_model")
        return GradeReport(artifact_valid, False, False, False, tuple(diagnostics))

    expected_predictions = _predict(test, coefficients)
    numerical_correct = _all_close(
        expected_predictions,
        [submitted_predictions[row_id] for row_id in expected_ids],
    )
    train_predictions = _predict(train, coefficients)
    residuals = [
        target - prediction
        for target, prediction in zip(_targets(train), train_predictions, strict=True)
    ]
    expected_values = {
        "train_rmse": _rmse(_targets(train), train_predictions),
        "test_rmse": _rmse(_targets(test), expected_predictions),
        "residual_mean": sum(residuals) / len(residuals),
        "residual_target_correlation": _correlation(residuals, _targets(train)),
    }
    for name, expected in expected_values.items():
        if not math.isclose(result[name], expected, abs_tol=_ABS_TOLERANCE, rel_tol=_ABS_TOLERANCE):
            diagnostics.append(f"incorrect_{name}")
            numerical_correct = False

    reference_errors = {
        model_id: _rmse(_targets(test), _predict(test, _fit(train, terms)))
        for model_id, terms in model_terms.items()
    }
    expected_selection = min(reference_errors, key=reference_errors.__getitem__)
    expected_conclusion = (
        "naa_and_cr_preferred" if expected_selection == "naa_and_cr" else "naa_only_preferred"
    )
    scientifically_valid = (
        selected == expected_selection and result["conclusion_code"] == expected_conclusion
    )
    if not scientifically_valid:
        diagnostics.append("selection_or_conclusion_not_supported")

    reproducible = numerical_correct and artifact_valid
    return GradeReport(
        artifact_valid,
        numerical_correct,
        scientifically_valid,
        reproducible,
        tuple(diagnostics),
    )


def _write_rows(path: Path, generator: random.Random, prefix: str, count: int) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        fields = ("point_id", "frequency_ppm", "naa_basis", "cr_basis", "observed_signal")
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for index in range(count):
            frequency = 0.5 + 3.7 * index / (count - 1)
            naa_basis = math.exp(-0.5 * ((frequency - 2.02) / 0.09) ** 2)
            cr_basis = math.exp(-0.5 * ((frequency - 3.03) / 0.08) ** 2)
            signal = 0.02 + 1.4 * naa_basis + 0.9 * cr_basis + generator.gauss(0.0, 0.01)
            writer.writerow(
                {
                    "point_id": f"{prefix}-{index:03d}",
                    "frequency_ppm": f"{frequency:.17g}",
                    "naa_basis": f"{naa_basis:.17g}",
                    "cr_basis": f"{cr_basis:.17g}",
                    "observed_signal": f"{signal:.17g}",
                }
            )


def _read_dataset(path: Path) -> list[dict[str, float | str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        expected_fields = (
            "point_id",
            "frequency_ppm",
            "naa_basis",
            "cr_basis",
            "observed_signal",
        )
        if tuple(reader.fieldnames or ()) != expected_fields:
            raise MRSSpectralFitError("dataset columns do not match schema")
        rows: list[dict[str, float | str]] = []
        for raw in reader:
            rows.append(
                {
                    "point_id": raw["point_id"],
                    "frequency_ppm": _finite_float(raw["frequency_ppm"]),
                    "naa_basis": _finite_float(raw["naa_basis"]),
                    "cr_basis": _finite_float(raw["cr_basis"]),
                    "observed_signal": _finite_float(raw["observed_signal"]),
                }
            )
    if not rows or len({row["point_id"] for row in rows}) != len(rows):
        raise MRSSpectralFitError("dataset must contain unique rows")
    return rows


def _read_result(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) != _RESULT_FIELDS:
        raise MRSSpectralFitError("result fields do not match schema")
    if not isinstance(value["coefficients"], dict):
        raise MRSSpectralFitError("coefficients must be an object")
    result = dict(value)
    result["coefficients"] = {
        str(name): _finite_float(coefficient) for name, coefficient in value["coefficients"].items()
    }
    for name in ("train_rmse", "test_rmse", "residual_mean", "residual_target_correlation"):
        result[name] = _finite_float(value[name])
    if isinstance(value["prediction_row_count"], bool) or not isinstance(
        value["prediction_row_count"], int
    ):
        raise MRSSpectralFitError("prediction_row_count must be an integer")
    return result


def _read_predictions(path: Path) -> dict[str, float]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != _PREDICTION_FIELDS:
            raise MRSSpectralFitError("prediction columns do not match schema")
        predictions: dict[str, float] = {}
        for row in reader:
            point_id = row["point_id"]
            if point_id in predictions:
                raise MRSSpectralFitError("duplicate prediction row ID")
            predictions[point_id] = _finite_float(row["predicted_signal"])
    return predictions


def _fit(rows: Sequence[dict[str, float | str]], terms: tuple[str, ...]) -> dict[str, float]:
    matrix = [[_term(row, term) for term in terms] for row in rows]
    targets = _targets(rows)
    gram = [
        [sum(vector[i] * vector[j] for vector in matrix) for j in range(len(terms))]
        for i in range(len(terms))
    ]
    rhs = [
        sum(vector[i] * target for vector, target in zip(matrix, targets, strict=True))
        for i in range(len(terms))
    ]
    solution = _solve_system(gram, rhs)
    return dict(zip(terms, solution, strict=True))


def _solve_system(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float]:
    augmented = [[*row, value] for row, value in zip(matrix, vector, strict=True)]
    size = len(augmented)
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise MRSSpectralFitError("singular design matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[column], strict=True)
            ]
    return [augmented[index][-1] for index in range(size)]


def _term(row: dict[str, float | str], name: str) -> float:
    return 1.0 if name == "intercept" else float(row[name])


def _targets(rows: Sequence[dict[str, float | str]]) -> list[float]:
    return [float(row["observed_signal"]) for row in rows]


def _predict(rows: Sequence[dict[str, float | str]], coefficients: dict[str, float]) -> list[float]:
    return [sum(_term(row, name) * value for name, value in coefficients.items()) for row in rows]


def _rmse(expected: Sequence[float], actual: Sequence[float]) -> float:
    if len(expected) != len(actual) or not expected:
        raise MRSSpectralFitError("RMSE inputs must have equal non-zero length")
    return math.sqrt(
        sum((left - right) ** 2 for left, right in zip(expected, actual, strict=True))
        / len(expected)
    )


def _correlation(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise MRSSpectralFitError("correlation inputs must have equal length")
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right, strict=True))
    left_scale = math.sqrt(sum((x - left_mean) ** 2 for x in left))
    right_scale = math.sqrt(sum((y - right_mean) ** 2 for y in right))
    if left_scale == 0.0 or right_scale == 0.0:
        return 0.0
    return numerator / (left_scale * right_scale)


def _all_close(left: Iterable[float], right: Iterable[float]) -> bool:
    left_values = list(left)
    right_values = list(right)
    return len(left_values) == len(right_values) and all(
        math.isclose(x, y, abs_tol=_ABS_TOLERANCE, rel_tol=_ABS_TOLERANCE)
        for x, y in zip(left_values, right_values, strict=True)
    )


def _finite_float(value: object) -> float:
    if isinstance(value, bool):
        raise MRSSpectralFitError("boolean is not numeric")
    if not isinstance(value, int | float | str):
        raise MRSSpectralFitError("value is not numeric")
    number = float(value)
    if not math.isfinite(number):
        raise MRSSpectralFitError("numeric values must be finite")
    return number
