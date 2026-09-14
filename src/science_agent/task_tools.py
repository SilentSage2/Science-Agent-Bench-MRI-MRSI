"""Fixed-path development bindings for the four implemented MRI/MRSI tasks."""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from science_agent.budget import BudgetUsage
from science_agent.contracts import Observation, TaskSpec
from science_agent.grading import GradeReport
from science_agent.tasks import (
    grade_mri_leakage,
    grade_mri_reconstruction,
    grade_mrs_fit,
    grade_mrsi_nuisance,
    solve_mri_leakage_reference,
    solve_mri_reconstruction_reference,
    solve_mrs_fit_reference,
    solve_mrsi_nuisance_reference,
)
from science_agent.tools import RegisteredTool, ToolRegistry, ToolResult
from science_agent.trajectory import sha256_file


class TaskBindingError(ValueError):
    """Raised when public task inputs cannot form a safe fixed-path binding."""


@dataclass(frozen=True, slots=True)
class ReferenceTaskBinding:
    """Development-only task boundary used to validate agent orchestration."""

    task: TaskSpec
    tools: ToolRegistry
    evaluator: Callable[[], GradeReport]


Solver = Callable[[Path, Path], None]

_DEFAULT_TOOL_MAXIMUM = BudgetUsage(
    tool_calls=1,
    wall_time_ms=60_000,
    artifact_bytes=1_048_576,
)


def bind_mrs_fit_reference(
    input_directory: Path,
    output_directory: Path,
    *,
    maximum_usage: BudgetUsage = _DEFAULT_TOOL_MAXIMUM,
) -> ReferenceTaskBinding:
    return _bind(
        input_directory=input_directory,
        output_directory=output_directory,
        expected_task_id="SAB-MRS-FIT-001",
        objective="Select the supported proton MRS basis model and report reproducible evidence.",
        tool_name="fit_mrs_basis_reference",
        required_artifacts=("result.json", "predictions.csv"),
        solver=solve_mrs_fit_reference,
        evaluator=lambda: grade_mrs_fit(input_directory, output_directory),
        maximum_usage=maximum_usage,
    )


def bind_mri_leakage_reference(
    input_directory: Path,
    output_directory: Path,
    *,
    maximum_usage: BudgetUsage = _DEFAULT_TOOL_MAXIMUM,
) -> ReferenceTaskBinding:
    return _bind(
        input_directory=input_directory,
        output_directory=output_directory,
        expected_task_id="SAB-MRI-LEAK-001",
        objective="Audit MRI/MRSI splits for subject, acquisition, temporal, and target leakage.",
        tool_name="audit_mri_split_reference",
        required_artifacts=("result.json",),
        solver=solve_mri_leakage_reference,
        evaluator=lambda: grade_mri_leakage(input_directory, output_directory),
        maximum_usage=maximum_usage,
    )


def bind_mri_reconstruction_reference(
    input_directory: Path,
    evaluator_directory: Path,
    output_directory: Path,
    *,
    maximum_usage: BudgetUsage = _DEFAULT_TOOL_MAXIMUM,
) -> ReferenceTaskBinding:
    return _bind(
        input_directory=input_directory,
        output_directory=output_directory,
        expected_task_id="SAB-MRI-RECON-001",
        objective="Reconstruct undersampled Cartesian MRI while preserving acquired k-space.",
        tool_name="reconstruct_mri_reference",
        required_artifacts=("result.json", "reconstruction.csv"),
        solver=solve_mri_reconstruction_reference,
        evaluator=lambda: grade_mri_reconstruction(
            input_directory, evaluator_directory, output_directory
        ),
        maximum_usage=maximum_usage,
    )


def bind_mrsi_nuisance_reference(
    input_directory: Path,
    evaluator_directory: Path,
    output_directory: Path,
    *,
    maximum_usage: BudgetUsage = _DEFAULT_TOOL_MAXIMUM,
) -> ReferenceTaskBinding:
    return _bind(
        input_directory=input_directory,
        output_directory=output_directory,
        expected_task_id="SAB-MRSI-NUIS-001",
        objective="Remove MRSI water/lipid nuisance while retaining metabolite signal.",
        tool_name="remove_mrsi_nuisance_reference",
        required_artifacts=("result.json", "corrected_spectra.csv"),
        solver=solve_mrsi_nuisance_reference,
        evaluator=lambda: grade_mrsi_nuisance(
            input_directory, evaluator_directory, output_directory
        ),
        maximum_usage=maximum_usage,
    )


def _bind(
    *,
    input_directory: Path,
    output_directory: Path,
    expected_task_id: str,
    objective: str,
    tool_name: str,
    required_artifacts: tuple[str, ...],
    solver: Solver,
    evaluator: Callable[[], GradeReport],
    maximum_usage: BudgetUsage,
) -> ReferenceTaskBinding:
    if maximum_usage.tool_calls != 1:
        raise TaskBindingError("task tool maximum must reserve exactly one tool call")
    metadata = _read_metadata(input_directory / "task.json", expected_task_id)
    task = TaskSpec(
        task_id=expected_task_id,
        schema_version=str(metadata["schema_version"]),
        objective=objective,
        allowed_tools=(tool_name,),
        required_artifacts=required_artifacts,
        metadata=metadata,
    )

    def handler(arguments: Mapping[str, Any]) -> ToolResult:
        started = time.monotonic_ns()
        if arguments:
            return ToolResult(
                Observation(
                    ok=False,
                    code="unexpected_tool_arguments",
                    payload={"expected": "empty_object"},
                    retryable=False,
                ),
                BudgetUsage(tool_calls=1, wall_time_ms=_elapsed_ms(started)),
            )
        if output_directory.exists():
            return ToolResult(
                Observation(ok=False, code="output_already_exists", retryable=False),
                BudgetUsage(tool_calls=1, wall_time_ms=_elapsed_ms(started)),
            )
        solver(input_directory, output_directory)
        artifacts = {
            path.name: sha256_file(path)
            for path in sorted(output_directory.iterdir())
            if path.is_file()
        }
        artifact_bytes = sum(
            path.stat().st_size for path in output_directory.iterdir() if path.is_file()
        )
        return ToolResult(
            Observation(
                ok=True,
                code="reference_artifacts_created",
                payload={"artifact_hashes": artifacts},
            ),
            BudgetUsage(
                tool_calls=1,
                wall_time_ms=_elapsed_ms(started),
                artifact_bytes=artifact_bytes,
            ),
        )

    return ReferenceTaskBinding(
        task=task,
        tools=ToolRegistry((RegisteredTool(tool_name, maximum_usage, handler),)),
        evaluator=evaluator,
    )


def _read_metadata(path: Path, expected_task_id: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TaskBindingError("task metadata is unreadable") from exc
    if not isinstance(value, dict):
        raise TaskBindingError("task metadata must be an object")
    if value.get("task_id") != expected_task_id:
        raise TaskBindingError("task metadata has the wrong task_id")
    schema_version = value.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version.strip():
        raise TaskBindingError("task metadata has no schema_version")
    return value


def _elapsed_ms(started_ns: int) -> int:
    return max(0, (time.monotonic_ns() - started_ns) // 1_000_000)
