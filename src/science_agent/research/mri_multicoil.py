"""Multi-coil Cartesian MRI reconstruction candidate with hidden-reference grading."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from science_agent.grading import GradeReport

TASK_ID = "SAB-MRI-RECON-MC-001"
SCHEMA_VERSION = "2"

ComplexArray = npt.NDArray[np.complex128]
RealArray = npt.NDArray[np.float64]
BoolArray = npt.NDArray[np.bool_]


class MulticoilMRIError(ValueError):
    """Raised when a research reconstruction instance or artifact is invalid."""


@dataclass(frozen=True, slots=True)
class ReconstructionMetrics:
    magnitude_nrmse: float
    gradient_nrmse: float
    sampled_kspace_residual: float


@dataclass(frozen=True, slots=True)
class BaselineResult:
    method: str
    metrics: ReconstructionMetrics


def create_multicoil_reconstruction_instance(
    input_directory: Path,
    evaluator_directory: Path,
    *,
    seed: int,
    matrix_size: int = 64,
    coils: int = 8,
    acceleration: float = 4.0,
    center_fraction: float = 0.125,
    relative_noise: float = 0.02,
) -> None:
    """Create noisy multi-coil k-space with evaluator-isolated ground truth."""
    if matrix_size < 32 or matrix_size % 2:
        raise MulticoilMRIError("matrix_size must be an even integer of at least 32")
    if coils < 4:
        raise MulticoilMRIError("at least four coils are required")
    if acceleration < 2.0 or acceleration > 12.0:
        raise MulticoilMRIError("acceleration must be in [2, 12]")
    if not 0.04 <= center_fraction <= 0.25:
        raise MulticoilMRIError("center_fraction must be in [0.04, 0.25]")
    if not 0.0 <= relative_noise <= 0.2:
        raise MulticoilMRIError("relative_noise must be in [0, 0.2]")

    input_directory.mkdir(parents=True, exist_ok=False)
    evaluator_directory.mkdir(parents=True, exist_ok=False)
    generator = np.random.default_rng(seed)
    reference = _complex_phantom(matrix_size, generator)
    sensitivities = _coil_sensitivities(matrix_size, coils)
    full_kspace = _forward(reference, sensitivities)
    mask = _variable_density_mask(
        matrix_size,
        acceleration=acceleration,
        center_fraction=center_fraction,
        generator=generator,
    )
    sampled_values = full_kspace[:, mask]
    signal_rms = float(np.sqrt(np.mean(np.abs(sampled_values) ** 2)))
    noise_standard_deviation = relative_noise * signal_rms
    noise = (
        noise_standard_deviation
        / math.sqrt(2.0)
        * (
            generator.standard_normal(full_kspace.shape)
            + 1j * generator.standard_normal(full_kspace.shape)
        )
    )
    measured = np.where(mask[None, :, :], full_kspace + noise, 0.0j)

    np.savez_compressed(
        input_directory / "acquisition.npz",
        kspace=measured.astype(np.complex64),
        mask=mask,
        sensitivities=sensitivities.astype(np.complex64),
    )
    task = {
        "task_id": TASK_ID,
        "schema_version": SCHEMA_VERSION,
        "domain": "noisy_multicoil_cartesian_mri_reconstruction",
        "matrix_size": matrix_size,
        "coil_count": coils,
        "nominal_acceleration": acceleration,
        "actual_sampled_fraction": float(mask.mean()),
        "center_fraction": center_fraction,
        "relative_noise": relative_noise,
        "allowed_methods": ["zero_filled", "sense_cg"],
        "sense_cg_regularization_range": [0.0001, 0.1],
        "sense_cg_iteration_range": [5, 80],
        "required_artifacts": ["result.json", "reconstruction.npz"],
    }
    (input_directory / "task.json").write_text(
        json.dumps(task, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    np.savez_compressed(
        evaluator_directory / "reference.npz",
        image=reference.astype(np.complex64),
        noiseless_kspace=full_kspace.astype(np.complex64),
    )
    evaluator_metadata = {
        "seed": seed,
        "generator_version": "multicoil-phantom-v1",
        "noise_standard_deviation": noise_standard_deviation,
    }
    (evaluator_directory / "metadata.json").write_text(
        json.dumps(evaluator_metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run_multicoil_reconstruction(
    input_directory: Path,
    output_directory: Path,
    *,
    method: str,
    regularization: float | None = None,
    iterations: int | None = None,
) -> None:
    """Run an allowlisted baseline using public acquisition data only."""
    task = _read_task(input_directory / "task.json")
    kspace, mask, sensitivities = _read_acquisition(input_directory / "acquisition.npz")
    if method == "zero_filled":
        if regularization is not None or iterations is not None:
            raise MulticoilMRIError("zero_filled accepts no hyperparameters")
        reconstruction = _adjoint(kspace, sensitivities)
        used_regularization = 0.0
        used_iterations = 0
    elif method == "sense_cg":
        if regularization is None or not 0.0001 <= regularization <= 0.1:
            raise MulticoilMRIError("sense_cg regularization must be in [0.0001, 0.1]")
        if iterations is None or not 5 <= iterations <= 80:
            raise MulticoilMRIError("sense_cg iterations must be in [5, 80]")
        reconstruction = _sense_cg(
            kspace,
            mask,
            sensitivities,
            regularization=regularization,
            iterations=iterations,
        )
        used_regularization = regularization
        used_iterations = iterations
    else:
        raise MulticoilMRIError("method is not allowlisted")

    residual = _sampled_kspace_residual(reconstruction, kspace, mask, sensitivities)
    if output_directory.exists():
        if not output_directory.is_dir() or any(output_directory.iterdir()):
            raise MulticoilMRIError("output directory must be empty")
    else:
        output_directory.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(
        output_directory / "reconstruction.npz",
        image=reconstruction.astype(np.complex64),
    )
    result = {
        "task_id": TASK_ID,
        "schema_version": SCHEMA_VERSION,
        "method": method,
        "regularization": used_regularization,
        "iterations": used_iterations,
        "reported_sampled_kspace_residual": residual,
        "conclusion_code": "reconstruction_complete",
        "matrix_size": int(task["matrix_size"]),
    }
    (output_directory / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def evaluate_multicoil_baselines(
    input_directory: Path,
    evaluator_directory: Path,
) -> tuple[BaselineResult, ...]:
    """Evaluate naive, conventional, and hidden-reference oracle baselines."""
    kspace, mask, sensitivities = _read_acquisition(input_directory / "acquisition.npz")
    reference, _ = _read_reference(evaluator_directory / "reference.npz")
    candidates = {
        "zero_filled": _adjoint(kspace, sensitivities),
        "sense_cg": _sense_cg(
            kspace,
            mask,
            sensitivities,
            regularization=0.003,
            iterations=40,
        ),
        "oracle_hidden_reference": reference,
    }
    return tuple(
        BaselineResult(
            method=method,
            metrics=_metrics(image, reference, kspace, mask, sensitivities),
        )
        for method, image in candidates.items()
    )


def grade_multicoil_reconstruction(
    input_directory: Path,
    evaluator_directory: Path,
    output_directory: Path,
) -> GradeReport:
    """Grade artifacts against hidden anatomy and conventional-task calibration."""
    try:
        task = _read_task(input_directory / "task.json")
        result = _read_result(output_directory / "result.json")
        reconstruction = _read_reconstruction(output_directory / "reconstruction.npz")
        kspace, mask, sensitivities = _read_acquisition(input_directory / "acquisition.npz")
        reference, _ = _read_reference(evaluator_directory / "reference.npz")
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return GradeReport(False, False, False, False, (f"artifact_error:{exc}",))

    size = int(task["matrix_size"])
    artifact_valid = bool(
        result.get("task_id") == TASK_ID
        and result.get("schema_version") == SCHEMA_VERSION
        and result.get("matrix_size") == size
        and reconstruction.shape == (size, size)
        and np.isfinite(reconstruction).all()
    )
    if not artifact_valid:
        return GradeReport(False, False, False, False, ("artifact_schema_or_shape_invalid",))

    metrics = _metrics(reconstruction, reference, kspace, mask, sensitivities)
    reported = _finite_float(result.get("reported_sampled_kspace_residual"))
    numerical_correct = math.isclose(
        reported,
        metrics.sampled_kspace_residual,
        rel_tol=1e-5,
        abs_tol=1e-7,
    )
    conventional = evaluate_multicoil_baselines(input_directory, evaluator_directory)[1].metrics
    scientifically_valid = (
        numerical_correct
        and result.get("conclusion_code") == "reconstruction_complete"
        and metrics.magnitude_nrmse <= conventional.magnitude_nrmse * 1.05
        and metrics.gradient_nrmse <= conventional.gradient_nrmse * 1.05
        and metrics.sampled_kspace_residual <= 0.08
    )
    diagnostics: list[str] = []
    if not numerical_correct:
        diagnostics.append("reported_residual_does_not_match")
    if metrics.magnitude_nrmse > conventional.magnitude_nrmse * 1.05:
        diagnostics.append("magnitude_nrmse_worse_than_conventional_tolerance")
    if metrics.gradient_nrmse > conventional.gradient_nrmse * 1.05:
        diagnostics.append("gradient_nrmse_worse_than_conventional_tolerance")
    if metrics.sampled_kspace_residual > 0.08:
        diagnostics.append("sampled_kspace_residual_too_high")
    if result.get("conclusion_code") != "reconstruction_complete":
        diagnostics.append("conclusion_not_supported")
    return GradeReport(
        artifact_valid=artifact_valid,
        numerical_correct=numerical_correct,
        scientifically_valid=scientifically_valid,
        reproducible=artifact_valid and numerical_correct,
        diagnostics=tuple(diagnostics),
        metrics={
            "magnitude_nrmse": metrics.magnitude_nrmse,
            "gradient_nrmse": metrics.gradient_nrmse,
            "sampled_kspace_residual": metrics.sampled_kspace_residual,
            "conventional_magnitude_nrmse": conventional.magnitude_nrmse,
            "conventional_gradient_nrmse": conventional.gradient_nrmse,
        },
    )


def _complex_phantom(size: int, generator: np.random.Generator) -> ComplexArray:
    axis = np.linspace(-1.0, 1.0, size, dtype=np.float64)
    x, y = np.meshgrid(axis, axis)
    magnitude = np.zeros((size, size), dtype=np.float64)
    ellipses = (
        (0.82, 0.69, 0.92, 0.0, 0.0, 0.0),
        (-0.36, 0.62, 0.86, 0.0, -0.02, 0.0),
        (0.22, 0.20, 0.31, -0.24, 0.02, -18.0),
        (0.18, 0.15, 0.22, 0.28, -0.24, 25.0),
        (-0.12, 0.12, 0.40, 0.0, 0.34, 0.0),
    )
    for amplitude, radius_x, radius_y, center_x, center_y, angle_degrees in ellipses:
        angle = math.radians(angle_degrees)
        rotated_x = (x - center_x) * math.cos(angle) + (y - center_y) * math.sin(angle)
        rotated_y = -(x - center_x) * math.sin(angle) + (y - center_y) * math.cos(angle)
        magnitude += amplitude * ((rotated_x / radius_x) ** 2 + (rotated_y / radius_y) ** 2 <= 1.0)
    for _ in range(3):
        center_x, center_y = generator.uniform(-0.45, 0.45, size=2)
        radius = float(generator.uniform(0.035, 0.09))
        amplitude = float(generator.uniform(-0.12, 0.18))
        magnitude += amplitude * ((x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2)
    clipped_magnitude: RealArray = np.asarray(np.clip(magnitude, 0.0, None), dtype=np.float64)
    clipped_magnitude /= float(clipped_magnitude.max())
    phase = 0.18 * x - 0.12 * y + 0.08 * x * y
    return np.asarray(clipped_magnitude * np.exp(1j * phase), dtype=np.complex128)


def _coil_sensitivities(size: int, coils: int) -> ComplexArray:
    axis = np.linspace(-1.0, 1.0, size, dtype=np.float64)
    x, y = np.meshgrid(axis, axis)
    maps: list[ComplexArray] = []
    for index in range(coils):
        angle = 2.0 * math.pi * index / coils
        center_x, center_y = 1.25 * math.cos(angle), 1.25 * math.sin(angle)
        distance_squared = (x - center_x) ** 2 + (y - center_y) ** 2
        magnitude = 1.0 / (distance_squared + 0.35)
        phase = np.exp(1j * math.pi * (0.18 * x * math.cos(angle) + 0.18 * y * math.sin(angle)))
        maps.append(np.asarray(magnitude * phase, dtype=np.complex128))
    sensitivities = np.stack(maps)
    normalization = np.sqrt(np.sum(np.abs(sensitivities) ** 2, axis=0))
    return np.asarray(sensitivities / normalization[None, :, :], dtype=np.complex128)


def _variable_density_mask(
    size: int,
    *,
    acceleration: float,
    center_fraction: float,
    generator: np.random.Generator,
) -> BoolArray:
    target_lines = max(1, int(round(size / acceleration)))
    center_lines = max(2, int(round(size * center_fraction)))
    center_lines = min(center_lines, target_lines)
    start = (size - center_lines) // 2
    selected = set(range(start, start + center_lines))
    candidates = np.array([index for index in range(size) if index not in selected])
    remaining = target_lines - len(selected)
    if remaining > 0:
        distance = np.abs(candidates - (size - 1) / 2.0)
        weights = np.exp(-((distance / (0.32 * size)) ** 2)) + 0.03
        chosen = generator.choice(
            candidates, size=remaining, replace=False, p=weights / weights.sum()
        )
        selected.update(int(value) for value in chosen)
    line_mask = np.zeros(size, dtype=np.bool_)
    line_mask[list(selected)] = True
    return np.repeat(line_mask[:, None], size, axis=1)


def _fft2c(image: ComplexArray) -> ComplexArray:
    return np.asarray(
        np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(image), norm="ortho")),
        dtype=np.complex128,
    )


def _ifft2c(kspace: ComplexArray) -> ComplexArray:
    return np.asarray(
        np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(kspace), norm="ortho")),
        dtype=np.complex128,
    )


def _forward(image: ComplexArray, sensitivities: ComplexArray) -> ComplexArray:
    return np.stack([_fft2c(sensitivity * image) for sensitivity in sensitivities])


def _adjoint(kspace: ComplexArray, sensitivities: ComplexArray) -> ComplexArray:
    coil_images = np.stack([_ifft2c(coil) for coil in kspace])
    return np.asarray(
        np.sum(np.conj(sensitivities) * coil_images, axis=0),
        dtype=np.complex128,
    )


def _sense_cg(
    kspace: ComplexArray,
    mask: BoolArray,
    sensitivities: ComplexArray,
    *,
    regularization: float,
    iterations: int,
) -> ComplexArray:
    rhs = _adjoint(kspace, sensitivities)

    def normal(image: ComplexArray) -> ComplexArray:
        encoded = _forward(image, sensitivities)
        data_term = _adjoint(np.where(mask[None, :, :], encoded, 0.0j), sensitivities)
        laplacian = (
            4.0 * image
            - np.roll(image, 1, axis=0)
            - np.roll(image, -1, axis=0)
            - np.roll(image, 1, axis=1)
            - np.roll(image, -1, axis=1)
        )
        return np.asarray(data_term + regularization * laplacian, dtype=np.complex128)

    image = rhs.copy()
    residual = rhs - normal(image)
    direction = residual.copy()
    residual_energy = float(np.vdot(residual, residual).real)
    epsilon = float(np.finfo(np.float64).eps)
    initial_energy = max(residual_energy, epsilon)
    for _ in range(iterations):
        normal_direction = normal(direction)
        denominator = float(np.vdot(direction, normal_direction).real)
        if denominator <= epsilon:
            break
        step = residual_energy / denominator
        image += step * direction
        residual -= step * normal_direction
        next_energy = float(np.vdot(residual, residual).real)
        if next_energy <= initial_energy * 1e-12:
            break
        direction = residual + (next_energy / residual_energy) * direction
        residual_energy = next_energy
    return np.asarray(image, dtype=np.complex128)


def _metrics(
    image: ComplexArray,
    reference: ComplexArray,
    measured: ComplexArray,
    mask: BoolArray,
    sensitivities: ComplexArray,
) -> ReconstructionMetrics:
    magnitude = np.abs(image)
    reference_magnitude = np.abs(reference)
    return ReconstructionMetrics(
        magnitude_nrmse=_nrmse(magnitude, reference_magnitude),
        gradient_nrmse=_gradient_nrmse(magnitude, reference_magnitude),
        sampled_kspace_residual=_sampled_kspace_residual(image, measured, mask, sensitivities),
    )


def _nrmse(actual: RealArray, reference: RealArray) -> float:
    denominator = float(np.linalg.norm(reference))
    if denominator == 0.0:
        raise MulticoilMRIError("reference has zero energy")
    return float(np.linalg.norm(actual - reference) / denominator)


def _gradient_nrmse(actual: RealArray, reference: RealArray) -> float:
    actual_gradient = np.concatenate(
        (np.diff(actual, axis=0).ravel(), np.diff(actual, axis=1).ravel())
    )
    reference_gradient = np.concatenate(
        (np.diff(reference, axis=0).ravel(), np.diff(reference, axis=1).ravel())
    )
    return _nrmse(actual_gradient, reference_gradient)


def _sampled_kspace_residual(
    image: ComplexArray,
    measured: ComplexArray,
    mask: BoolArray,
    sensitivities: ComplexArray,
) -> float:
    predicted = _forward(image, sensitivities)
    difference = predicted[:, mask] - measured[:, mask]
    denominator = float(np.linalg.norm(measured[:, mask]))
    if denominator == 0.0:
        raise MulticoilMRIError("measured k-space has zero energy")
    return float(np.linalg.norm(difference) / denominator)


def _read_task(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("task_id") != TASK_ID:
        raise MulticoilMRIError("task metadata is invalid")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise MulticoilMRIError("task schema version is unsupported")
    return value


def _read_acquisition(path: Path) -> tuple[ComplexArray, BoolArray, ComplexArray]:
    with np.load(path, allow_pickle=False) as data:
        if set(data.files) != {"kspace", "mask", "sensitivities"}:
            raise MulticoilMRIError("acquisition fields are invalid")
        kspace = np.asarray(data["kspace"], dtype=np.complex128)
        mask = np.asarray(data["mask"], dtype=np.bool_)
        sensitivities = np.asarray(data["sensitivities"], dtype=np.complex128)
    if kspace.ndim != 3 or sensitivities.shape != kspace.shape:
        raise MulticoilMRIError("coil arrays must have equal three-dimensional shape")
    if mask.shape != kspace.shape[1:] or mask.ndim != 2:
        raise MulticoilMRIError("mask shape is invalid")
    if not np.isfinite(kspace).all() or not np.isfinite(sensitivities).all():
        raise MulticoilMRIError("acquisition contains non-finite values")
    if np.any(kspace[:, ~mask] != 0.0):
        raise MulticoilMRIError("unsampled k-space must be zero")
    return kspace, mask, sensitivities


def _read_reference(path: Path) -> tuple[ComplexArray, ComplexArray]:
    with np.load(path, allow_pickle=False) as data:
        if set(data.files) != {"image", "noiseless_kspace"}:
            raise MulticoilMRIError("reference fields are invalid")
        image = np.asarray(data["image"], dtype=np.complex128)
        kspace = np.asarray(data["noiseless_kspace"], dtype=np.complex128)
    return image, kspace


def _read_reconstruction(path: Path) -> ComplexArray:
    with np.load(path, allow_pickle=False) as data:
        if set(data.files) != {"image"}:
            raise MulticoilMRIError("reconstruction fields are invalid")
        return np.asarray(data["image"], dtype=np.complex128)


def _read_result(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise MulticoilMRIError("result must be an object")
    required = {
        "task_id",
        "schema_version",
        "method",
        "regularization",
        "iterations",
        "reported_sampled_kspace_residual",
        "conclusion_code",
        "matrix_size",
    }
    if set(value) != required:
        raise MulticoilMRIError("result fields are invalid")
    return value


def _finite_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise MulticoilMRIError("reported value must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise MulticoilMRIError("reported value must be finite")
    return result
