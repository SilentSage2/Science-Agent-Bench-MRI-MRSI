"""Complex MRSI nuisance-removal candidate with hidden metabolite-retention grading."""

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

TASK_ID = "SAB-MRSI-NUIS-CX-001"
SCHEMA_VERSION = "2"

ComplexArray = npt.NDArray[np.complex128]
RealArray = npt.NDArray[np.float64]


class ComplexMRSIError(ValueError):
    """Raised when a research MRSI instance or artifact is invalid."""


@dataclass(frozen=True, slots=True)
class MRSIMetrics:
    nuisance_residual_ratio: float
    metabolite_retention_nrmse: float
    spectral_nrmse: float


@dataclass(frozen=True, slots=True)
class MRSIBaselineResult:
    method: str
    metrics: MRSIMetrics


def create_complex_mrsi_instance(
    input_directory: Path,
    evaluator_directory: Path,
    *,
    seed: int,
    grid_size: int = 4,
    spectral_points: int = 256,
    difficulty: str = "moderate",
) -> None:
    """Create complex spectra with evaluator-isolated clean and nuisance components."""
    if grid_size < 3:
        raise ComplexMRSIError("grid_size must be at least 3")
    if spectral_points < 128:
        raise ComplexMRSIError("spectral_points must be at least 128")
    settings = {
        "easy": (0.018, 0.10, 0.010, 0.015),
        "moderate": (0.035, 0.22, 0.020, 0.025),
        "hard": (0.060, 0.38, 0.035, 0.040),
    }
    if difficulty not in settings:
        raise ComplexMRSIError("difficulty must be easy, moderate, or hard")
    max_shift, max_phase, linewidth_jitter, noise_fraction = settings[difficulty]
    input_directory.mkdir(parents=True, exist_ok=False)
    evaluator_directory.mkdir(parents=True, exist_ok=False)

    generator = np.random.default_rng(seed)
    ppm = np.linspace(0.5, 5.0, spectral_points, dtype=np.float64)
    nominal_water = _lorentzian(ppm, 4.70, 0.035)
    nominal_lipid = _lorentzian(ppm, 1.30, 0.16)
    voxel_count = grid_size * grid_size
    observed = np.empty((voxel_count, spectral_points), dtype=np.complex128)
    clean = np.empty_like(observed)
    nuisance = np.empty_like(observed)
    baseline = np.empty_like(observed)
    shifts = np.empty(voxel_count, dtype=np.float64)

    for index in range(voxel_count):
        y, x = divmod(index, grid_size)
        spatial_x = 2.0 * x / (grid_size - 1) - 1.0
        spatial_y = 2.0 * y / (grid_size - 1) - 1.0
        shift = max_shift * (0.55 * spatial_x - 0.35 * spatial_y) + generator.normal(
            0.0, max_shift * 0.12
        )
        zero_phase = max_phase * (0.6 * spatial_x + 0.4 * spatial_y)
        first_phase = max_phase * 0.45 * (spatial_x - spatial_y)
        phase_ramp = np.exp(1j * (zero_phase + first_phase * (ppm - 2.75)))
        linewidth_scale = 1.0 + generator.normal(0.0, linewidth_jitter)

        metabolite = (
            (0.80 + 0.10 * spatial_y) * _lorentzian(ppm, 2.02 + shift, 0.045)
            + (0.58 + 0.08 * spatial_x) * _lorentzian(ppm, 3.03 + shift, 0.040)
            + (0.36 - 0.05 * spatial_y) * _lorentzian(ppm, 3.20 + shift, 0.048)
            + (0.28 + 0.04 * spatial_x) * _lorentzian(ppm, 2.35 + shift, 0.075)
        ) * phase_ramp
        water_shape = _mixed_lineshape(
            ppm, 4.70 + shift, 0.035 * linewidth_scale, gaussian_fraction=0.22
        )
        lipid_shape = _mixed_lineshape(
            ppm, 1.30 + 0.65 * shift, 0.16 * linewidth_scale, gaussian_fraction=0.32
        )
        nuisance_phase = np.exp(1j * (zero_phase + 0.4 + first_phase * (ppm - 2.75)))
        nuisance_component = (
            (5.0 + 0.7 * spatial_x) * water_shape + (2.4 + 0.5 * spatial_y) * lipid_shape
        ) * nuisance_phase
        normalized_ppm = (ppm - ppm.mean()) / np.ptp(ppm)
        baseline_component = (
            (0.028 + 0.012j)
            + (0.020 * spatial_x - 0.014j * spatial_y) * normalized_ppm
            + (0.018 - 0.008j) * normalized_ppm**2
        )
        signal_scale = float(np.sqrt(np.mean(np.abs(metabolite) ** 2)))
        noise = (
            noise_fraction
            * signal_scale
            / math.sqrt(2.0)
            * (
                generator.standard_normal(spectral_points)
                + 1j * generator.standard_normal(spectral_points)
            )
        )
        clean[index] = metabolite
        nuisance[index] = nuisance_component
        baseline[index] = baseline_component
        observed[index] = metabolite + nuisance_component + baseline_component + noise
        shifts[index] = shift

    np.savez_compressed(
        input_directory / "spectra.npz",
        ppm=ppm,
        observed=observed.astype(np.complex64),
        nominal_water=nominal_water.astype(np.complex64),
        nominal_lipid=nominal_lipid.astype(np.complex64),
    )
    task = {
        "task_id": TASK_ID,
        "schema_version": SCHEMA_VERSION,
        "domain": "complex_proton_mrsi_nuisance_removal",
        "difficulty": difficulty,
        "grid_size": grid_size,
        "spectral_points": spectral_points,
        "spectral_axis": {
            "nucleus": "1H",
            "domain": "frequency",
            "units": "ppm",
            "minimum_ppm": 0.5,
            "maximum_ppm": 5.0,
            "storage_order": "ascending",
            "display_order": "descending",
            "inclusive_endpoints": True,
            "nominal_field_t": 3.0,
            "spectrometer_frequency_mhz": 127.73243676,
            "represented_span_hz": 574.79596542,
            "dwell_time_s": None,
            "sampling_representation": "frequency_domain_grid_inclusive_endpoints",
        },
        "allowed_methods": ["fixed_projection", "adaptive_projection"],
        "adaptive_shift_limit_ppm": 0.08,
        "adaptive_shift_steps_range": [5, 41],
        "adaptive_shift_steps_must_be_odd": True,
        "required_artifacts": ["result.json", "corrected_spectra.npz"],
    }
    (input_directory / "task.json").write_text(
        json.dumps(task, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    np.savez_compressed(
        evaluator_directory / "reference.npz",
        clean=clean.astype(np.complex64),
        nuisance=nuisance.astype(np.complex64),
        baseline=baseline.astype(np.complex64),
        frequency_shift_ppm=shifts,
    )
    (evaluator_directory / "metadata.json").write_text(
        json.dumps(
            {"generator_version": "complex-mrsi-nuisance-v1", "seed": seed},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def run_complex_mrsi_nuisance_removal(
    input_directory: Path,
    output_directory: Path,
    *,
    method: str,
    shift_steps: int | None = None,
) -> None:
    """Run an allowlisted nuisance-removal method using public spectra only."""
    task = _read_task(input_directory / "task.json")
    ppm, observed, nominal_water, nominal_lipid = _read_spectra(input_directory / "spectra.npz")
    if method == "fixed_projection":
        if shift_steps is not None:
            raise ComplexMRSIError("fixed_projection accepts no hyperparameters")
        corrected = _project_nuisance(
            ppm, observed, shift_limit=0.0, shift_steps=1, width_scales=(1.0,)
        )
        used_steps = 1
    elif method == "adaptive_projection":
        if shift_steps is None or not 5 <= shift_steps <= 41 or shift_steps % 2 == 0:
            raise ComplexMRSIError("adaptive shift_steps must be an odd integer in [5, 41]")
        corrected = _project_nuisance(
            ppm,
            observed,
            shift_limit=float(task["adaptive_shift_limit_ppm"]),
            shift_steps=shift_steps,
            width_scales=(0.8, 1.0, 1.2),
        )
        used_steps = shift_steps
    else:
        raise ComplexMRSIError("method is not allowlisted")

    public_residual = _public_nuisance_residual(observed, corrected, nominal_water, nominal_lipid)
    _prepare_output_directory(output_directory)
    np.savez_compressed(
        output_directory / "corrected_spectra.npz",
        corrected=corrected.astype(np.complex64),
    )
    result = {
        "task_id": TASK_ID,
        "schema_version": SCHEMA_VERSION,
        "method": method,
        "shift_steps": used_steps,
        "voxel_count": int(observed.shape[0]),
        "reported_public_nuisance_residual": public_residual,
        "conclusion_code": "nuisance_removal_complete",
    }
    (output_directory / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def evaluate_complex_mrsi_baselines(
    input_directory: Path,
    evaluator_directory: Path,
) -> tuple[MRSIBaselineResult, ...]:
    """Evaluate naive, conventional, and evaluator-only oracle baselines."""
    ppm, observed, _, _ = _read_spectra(input_directory / "spectra.npz")
    clean, nuisance, baseline = _read_reference(evaluator_directory / "reference.npz")
    candidates = {
        "fixed_projection": _project_nuisance(
            ppm, observed, shift_limit=0.0, shift_steps=1, width_scales=(1.0,)
        ),
        "adaptive_projection": _project_nuisance(
            ppm, observed, shift_limit=0.08, shift_steps=21, width_scales=(0.8, 1.0, 1.2)
        ),
        "oracle_hidden_components": observed - nuisance - baseline,
    }
    return tuple(
        MRSIBaselineResult(method, _metrics(ppm, candidate, clean, nuisance, baseline))
        for method, candidate in candidates.items()
    )


def grade_complex_mrsi_nuisance(
    input_directory: Path,
    evaluator_directory: Path,
    output_directory: Path,
) -> GradeReport:
    """Grade nuisance removal without exposing clean metabolites or true nuisance."""
    try:
        task = _read_task(input_directory / "task.json")
        result = _read_result(output_directory / "result.json")
        corrected = _read_corrected(output_directory / "corrected_spectra.npz")
        ppm, observed, nominal_water, nominal_lipid = _read_spectra(input_directory / "spectra.npz")
        clean, nuisance, baseline = _read_reference(evaluator_directory / "reference.npz")
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return GradeReport(False, False, False, False, (f"artifact_error:{exc}",))

    expected_shape = (int(task["grid_size"]) ** 2, int(task["spectral_points"]))
    artifact_valid = bool(
        result.get("task_id") == TASK_ID
        and result.get("schema_version") == SCHEMA_VERSION
        and result.get("voxel_count") == expected_shape[0]
        and corrected.shape == expected_shape
        and np.isfinite(corrected).all()
    )
    if not artifact_valid:
        return GradeReport(False, False, False, False, ("artifact_schema_or_shape_invalid",))
    public_residual = _public_nuisance_residual(observed, corrected, nominal_water, nominal_lipid)
    reported = _finite_float(result.get("reported_public_nuisance_residual"))
    numerical_correct = math.isclose(reported, public_residual, rel_tol=1e-5, abs_tol=1e-7)
    metrics = _metrics(ppm, corrected, clean, nuisance, baseline)
    conventional = evaluate_complex_mrsi_baselines(input_directory, evaluator_directory)[1].metrics
    scientifically_valid = bool(
        numerical_correct
        and result.get("conclusion_code") == "nuisance_removal_complete"
        and metrics.nuisance_residual_ratio
        <= max(0.20, conventional.nuisance_residual_ratio * 1.05)
        and metrics.metabolite_retention_nrmse
        <= max(0.25, conventional.metabolite_retention_nrmse * 1.05)
        and metrics.spectral_nrmse <= max(0.25, conventional.spectral_nrmse * 1.05)
    )
    diagnostics: list[str] = []
    if not numerical_correct:
        diagnostics.append("reported_public_residual_does_not_match")
    if metrics.nuisance_residual_ratio > max(0.20, conventional.nuisance_residual_ratio * 1.05):
        diagnostics.append("nuisance_suppression_worse_than_conventional_tolerance")
    if metrics.metabolite_retention_nrmse > max(
        0.25, conventional.metabolite_retention_nrmse * 1.05
    ):
        diagnostics.append("metabolite_retention_worse_than_conventional_tolerance")
    if metrics.spectral_nrmse > max(0.25, conventional.spectral_nrmse * 1.05):
        diagnostics.append("spectral_nrmse_worse_than_conventional_tolerance")
    if result.get("conclusion_code") != "nuisance_removal_complete":
        diagnostics.append("conclusion_not_supported")
    return GradeReport(
        artifact_valid,
        numerical_correct,
        scientifically_valid,
        artifact_valid and numerical_correct,
        tuple(diagnostics),
        {
            "nuisance_residual_ratio": metrics.nuisance_residual_ratio,
            "metabolite_retention_nrmse": metrics.metabolite_retention_nrmse,
            "spectral_nrmse": metrics.spectral_nrmse,
            "conventional_nuisance_residual_ratio": conventional.nuisance_residual_ratio,
            "conventional_metabolite_retention_nrmse": conventional.metabolite_retention_nrmse,
        },
    )


def _project_nuisance(
    ppm: RealArray,
    observed: ComplexArray,
    *,
    shift_limit: float,
    shift_steps: int,
    width_scales: tuple[float, ...],
) -> ComplexArray:
    nuisance_mask = (ppm >= 4.25) | (ppm <= 1.72)
    nuisance_indices = np.flatnonzero(nuisance_mask)
    normalized = (ppm - ppm.mean()) / np.ptp(ppm)
    shifts = np.linspace(-shift_limit, shift_limit, shift_steps)
    corrected = np.empty_like(observed)
    for voxel_index, spectrum in enumerate(observed):
        best_error = math.inf
        best_model: ComplexArray | None = None
        for shift in shifts:
            for width_scale in width_scales:
                water = _lorentzian(ppm, 4.70 + float(shift), 0.035 * width_scale)
                lipid = _lorentzian(ppm, 1.30 + 0.65 * float(shift), 0.16 * width_scale)
                if shift_steps == 1 and len(width_scales) == 1:
                    design = np.asarray(np.column_stack((water, lipid)), dtype=np.complex128)
                else:
                    water_gaussian = _gaussian(ppm, 4.70 + float(shift), 0.035 * width_scale * 1.35)
                    lipid_gaussian = _gaussian(
                        ppm, 1.30 + 0.65 * float(shift), 0.16 * width_scale * 1.35
                    )
                    design = np.asarray(
                        np.column_stack(
                            (
                                water,
                                water_gaussian,
                                normalized * water,
                                normalized * water_gaussian,
                                lipid,
                                lipid_gaussian,
                                normalized * lipid,
                                normalized * lipid_gaussian,
                            )
                        ),
                        dtype=np.complex128,
                    )
                selected_design = np.take(design, nuisance_indices, axis=0)
                selected_spectrum = np.take(spectrum, nuisance_indices)
                coefficients, _, _, _ = np.linalg.lstsq(
                    selected_design, selected_spectrum, rcond=1e-8
                )
                if not np.isfinite(coefficients).all() or np.max(np.abs(coefficients)) > 100.0:
                    continue
                model = np.asarray(
                    sum(
                        (
                            coefficient * column
                            for coefficient, column in zip(coefficients, design.T, strict=True)
                        ),
                        start=np.zeros_like(ppm, dtype=np.complex128),
                    ),
                    dtype=np.complex128,
                )
                error = float(np.linalg.norm((spectrum - model)[nuisance_mask]))
                if error < best_error:
                    best_error = error
                    best_model = model
        if best_model is None:
            raise ComplexMRSIError("adaptive nuisance fit produced no candidate")
        corrected[voxel_index] = spectrum - best_model
    return corrected


def _metrics(
    ppm: RealArray,
    corrected: ComplexArray,
    clean: ComplexArray,
    nuisance: ComplexArray,
    baseline: ComplexArray,
) -> MRSIMetrics:
    nuisance_mask = (ppm >= 4.25) | (ppm <= 1.72)
    metabolite_mask = ((ppm >= 1.82) & (ppm <= 2.55)) | ((ppm >= 2.86) & (ppm <= 3.38))
    nuisance_error = corrected[:, nuisance_mask] - clean[:, nuisance_mask]
    nuisance_energy = nuisance[:, nuisance_mask] + baseline[:, nuisance_mask]
    return MRSIMetrics(
        nuisance_residual_ratio=_ratio_norm(nuisance_error, nuisance_energy),
        metabolite_retention_nrmse=_ratio_norm(
            corrected[:, metabolite_mask] - clean[:, metabolite_mask],
            clean[:, metabolite_mask],
        ),
        spectral_nrmse=_ratio_norm(corrected - clean, clean),
    )


def _public_nuisance_residual(
    observed: ComplexArray,
    corrected: ComplexArray,
    nominal_water: ComplexArray,
    nominal_lipid: ComplexArray,
) -> float:
    templates = np.column_stack((nominal_water, nominal_lipid))
    before = 0.0
    after = 0.0
    for before_spectrum, after_spectrum in zip(observed, corrected, strict=True):
        before_coefficients, _, _, _ = np.linalg.lstsq(templates, before_spectrum, rcond=None)
        after_coefficients, _, _, _ = np.linalg.lstsq(templates, after_spectrum, rcond=None)
        before += float(np.linalg.norm(before_coefficients) ** 2)
        after += float(np.linalg.norm(after_coefficients) ** 2)
    return math.sqrt(after / max(before, float(np.finfo(np.float64).eps)))


def _lorentzian(ppm: RealArray, center: float, width: float) -> ComplexArray:
    return np.asarray(1.0 / (1.0 + 1j * (ppm - center) / width), dtype=np.complex128)


def _mixed_lineshape(
    ppm: RealArray,
    center: float,
    width: float,
    *,
    gaussian_fraction: float,
) -> ComplexArray:
    lorentzian = _lorentzian(ppm, center, width)
    gaussian = np.exp(-0.5 * ((ppm - center) / (width * 1.35)) ** 2).astype(np.complex128)
    return np.asarray(
        (1.0 - gaussian_fraction) * lorentzian + gaussian_fraction * gaussian,
        dtype=np.complex128,
    )


def _gaussian(ppm: RealArray, center: float, width: float) -> ComplexArray:
    return np.asarray(np.exp(-0.5 * ((ppm - center) / width) ** 2), dtype=np.complex128)


def _ratio_norm(numerator: ComplexArray, denominator: ComplexArray) -> float:
    denominator_norm = float(np.linalg.norm(denominator))
    if denominator_norm == 0.0:
        raise ComplexMRSIError("metric denominator has zero energy")
    return float(np.linalg.norm(numerator) / denominator_norm)


def _prepare_output_directory(path: Path) -> None:
    if path.exists():
        if not path.is_dir() or any(path.iterdir()):
            raise ComplexMRSIError("output directory must be empty")
    else:
        path.mkdir(parents=True, exist_ok=False)


def _read_task(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(value, dict)
        or value.get("task_id") != TASK_ID
        or value.get("schema_version") != SCHEMA_VERSION
    ):
        raise ComplexMRSIError("task metadata is invalid")
    return value


def _read_spectra(path: Path) -> tuple[RealArray, ComplexArray, ComplexArray, ComplexArray]:
    with np.load(path, allow_pickle=False) as data:
        if set(data.files) != {"ppm", "observed", "nominal_water", "nominal_lipid"}:
            raise ComplexMRSIError("spectra fields are invalid")
        ppm = np.asarray(data["ppm"], dtype=np.float64)
        observed = np.asarray(data["observed"], dtype=np.complex128)
        water = np.asarray(data["nominal_water"], dtype=np.complex128)
        lipid = np.asarray(data["nominal_lipid"], dtype=np.complex128)
    if ppm.ndim != 1 or observed.ndim != 2 or observed.shape[1] != ppm.size:
        raise ComplexMRSIError("spectra shapes are invalid")
    if water.shape != ppm.shape or lipid.shape != ppm.shape:
        raise ComplexMRSIError("nominal template shapes are invalid")
    if not all(np.isfinite(item).all() for item in (ppm, observed, water, lipid)):
        raise ComplexMRSIError("spectra contain non-finite values")
    return ppm, observed, water, lipid


def _read_reference(path: Path) -> tuple[ComplexArray, ComplexArray, ComplexArray]:
    with np.load(path, allow_pickle=False) as data:
        if set(data.files) != {"clean", "nuisance", "baseline", "frequency_shift_ppm"}:
            raise ComplexMRSIError("reference fields are invalid")
        clean = np.asarray(data["clean"], dtype=np.complex128)
        nuisance = np.asarray(data["nuisance"], dtype=np.complex128)
        baseline = np.asarray(data["baseline"], dtype=np.complex128)
    if clean.shape != nuisance.shape or clean.shape != baseline.shape:
        raise ComplexMRSIError("reference shapes are invalid")
    return clean, nuisance, baseline


def _read_corrected(path: Path) -> ComplexArray:
    with np.load(path, allow_pickle=False) as data:
        if set(data.files) != {"corrected"}:
            raise ComplexMRSIError("corrected spectra fields are invalid")
        return np.asarray(data["corrected"], dtype=np.complex128)


def _read_result(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "task_id",
        "schema_version",
        "method",
        "shift_steps",
        "voxel_count",
        "reported_public_nuisance_residual",
        "conclusion_code",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ComplexMRSIError("result fields are invalid")
    return value


def _finite_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ComplexMRSIError("reported value must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ComplexMRSIError("reported value must be finite")
    return result
