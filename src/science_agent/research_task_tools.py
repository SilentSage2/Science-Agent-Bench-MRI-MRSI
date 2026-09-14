"""Containerized policy binding for the multi-coil MRI research candidate."""

from __future__ import annotations

import json
import shutil
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from science_agent.budget import BudgetUsage
from science_agent.container_executor import ContainerRequest, ContainerResult
from science_agent.contracts import Observation, TaskSpec
from science_agent.grading import GradeReport
from science_agent.research.mri_multicoil import TASK_ID, grade_multicoil_reconstruction
from science_agent.tools import RegisteredTool, ToolRegistry, ToolResult


class ResearchTaskBindingError(ValueError):
    """Raised when a research task cannot be bound safely."""


class ContainerExecutor(Protocol):
    def execute(self, request: ContainerRequest) -> ContainerResult: ...


@dataclass(frozen=True, slots=True)
class MulticoilResearchBinding:
    task: TaskSpec
    tools: ToolRegistry
    evaluator: Callable[[], GradeReport]


def bind_multicoil_reconstruction(
    input_directory: Path,
    evaluator_directory: Path,
    output_directory: Path,
    work_directory: Path,
    executor: ContainerExecutor,
) -> MulticoilResearchBinding:
    """Bind fixed host paths while leaving only scientific choices to the policy."""
    metadata = _read_metadata(input_directory / "task.json")
    if output_directory.exists() or work_directory.exists():
        raise ResearchTaskBindingError("output and work directories must not exist")
    work_directory.mkdir(parents=True, exist_ok=False)
    attempts = 0

    def handler(arguments: Mapping[str, Any]) -> ToolResult:
        nonlocal attempts
        started = time.monotonic_ns()
        try:
            argv = _candidate_argv(arguments)
        except ResearchTaskBindingError as exc:
            return ToolResult(
                Observation(
                    ok=False,
                    code="invalid_reconstruction_choice",
                    payload={"reason": str(exc)},
                    retryable=True,
                ),
                BudgetUsage(tool_calls=1, wall_time_ms=_elapsed_ms(started)),
            )
        if output_directory.exists():
            return ToolResult(
                Observation(ok=False, code="output_already_finalized", retryable=False),
                BudgetUsage(tool_calls=1, wall_time_ms=_elapsed_ms(started)),
            )
        attempts += 1
        attempt_output = work_directory / f"attempt-{attempts:03d}"
        result = executor.execute(ContainerRequest(input_directory, attempt_output, argv))
        usage = BudgetUsage(
            tool_calls=1,
            wall_time_ms=result.duration_ms,
            artifact_bytes=result.artifact_bytes,
        )
        if result.exit_code != 0:
            return ToolResult(
                Observation(
                    ok=False,
                    code="container_reconstruction_failed",
                    payload={"exit_code": result.exit_code},
                    retryable=True,
                ),
                usage,
            )
        payload = json.loads((attempt_output / "result.json").read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ResearchTaskBindingError("container result must be an object")
        shutil.copytree(attempt_output, output_directory)
        return ToolResult(
            Observation(
                ok=True,
                code="reconstruction_artifacts_created",
                payload={
                    "method": payload.get("method"),
                    "sampled_kspace_residual": payload.get("reported_sampled_kspace_residual"),
                    "artifact_hashes": result.artifact_hashes,
                },
            ),
            usage,
        )

    task = TaskSpec(
        task_id=TASK_ID,
        schema_version=str(metadata["schema_version"]),
        objective=(
            "Reconstruct noisy undersampled multi-coil Cartesian MRI without silently "
            "violating the acquired-data model or overstating scientific validity."
        ),
        allowed_tools=("reconstruct_multicoil_mri",),
        required_artifacts=("result.json", "reconstruction.npz"),
        metadata=metadata,
    )
    maximum = BudgetUsage(tool_calls=1, wall_time_ms=60_000, artifact_bytes=4_194_304)
    return MulticoilResearchBinding(
        task=task,
        tools=ToolRegistry((RegisteredTool(task.allowed_tools[0], maximum, handler),)),
        evaluator=lambda: grade_multicoil_reconstruction(
            input_directory, evaluator_directory, output_directory
        ),
    )


def _candidate_argv(arguments: Mapping[str, Any]) -> tuple[str, ...]:
    method = arguments.get("method")
    if method == "zero_filled":
        if set(arguments) != {"method"}:
            raise ResearchTaskBindingError("zero_filled accepts only method")
        return (
            "python",
            "-m",
            "science_agent.research.mri_multicoil_runner",
            "--method",
            "zero_filled",
        )
    if method != "sense_cg" or set(arguments) != {"method", "regularization", "iterations"}:
        raise ResearchTaskBindingError("sense_cg requires method, regularization, and iterations")
    regularization = arguments["regularization"]
    iterations = arguments["iterations"]
    if isinstance(regularization, bool) or not isinstance(regularization, int | float):
        raise ResearchTaskBindingError("regularization must be numeric")
    if isinstance(iterations, bool) or not isinstance(iterations, int):
        raise ResearchTaskBindingError("iterations must be an integer")
    regularization_value = float(regularization)
    if not 0.0001 <= regularization_value <= 0.1:
        raise ResearchTaskBindingError("regularization is outside [0.0001, 0.1]")
    if not 5 <= iterations <= 80:
        raise ResearchTaskBindingError("iterations is outside [5, 80]")
    return (
        "python",
        "-m",
        "science_agent.research.mri_multicoil_runner",
        "--method",
        "sense_cg",
        "--regularization",
        format(regularization_value, ".17g"),
        "--iterations",
        str(iterations),
    )


def _read_metadata(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("task_id") != TASK_ID:
        raise ResearchTaskBindingError("task metadata is invalid")
    return value


def _elapsed_ms(started_ns: int) -> int:
    return max(0, (time.monotonic_ns() - started_ns) // 1_000_000)
