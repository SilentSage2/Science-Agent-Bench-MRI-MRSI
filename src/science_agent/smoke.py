"""Offline end-to-end smoke benchmark with a deterministic scripted policy."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from science_agent.budget import BudgetLedger, BudgetSpec, BudgetUsage
from science_agent.grading import GradeReport
from science_agent.state import AgentPhase, AgentStateMachine
from science_agent.tasks import (
    create_mri_leakage_fixture,
    create_mri_reconstruction_fixture,
    create_mrs_fit_fixture,
    grade_mri_leakage,
    grade_mri_reconstruction,
    grade_mrs_fit,
    solve_mri_leakage_reference,
    solve_mri_reconstruction_reference,
    solve_mrs_fit_reference,
)
from science_agent.trajectory import TrajectoryEvent, TrajectoryWriter, sha256_file


@dataclass(frozen=True, slots=True)
class Condition:
    name: str
    planning: bool


CONDITIONS = (
    Condition("reactive", False),
    Condition("plan_only", True),
    Condition("plan_retry_replan", True),
)


def run_smoke(output_root: Path) -> dict[str, object]:
    """Run two deterministic tasks under all three controller conditions."""
    output_root.mkdir(parents=True, exist_ok=False)
    task_definitions: tuple[
        tuple[
            str,
            Callable[[Path], None],
            Callable[[Path, Path], None],
            Callable[[Path, Path], GradeReport],
        ],
        ...,
    ] = (
        (
            "SAB-MRS-FIT-001-dev-1",
            lambda path: create_mrs_fit_fixture(path, seed=1701),
            solve_mrs_fit_reference,
            grade_mrs_fit,
        ),
        (
            "SAB-MRI-LEAK-001-dev-1",
            lambda path: create_mri_leakage_fixture(path, seed=2301, include_violations=True),
            solve_mri_leakage_reference,
            grade_mri_leakage,
        ),
        (
            "SAB-MRI-RECON-001-dev-1",
            lambda path: create_mri_reconstruction_fixture(
                path,
                path.parent / "evaluator",
                seed=3101,
                matrix_size=8,
            ),
            solve_mri_reconstruction_reference,
            lambda inputs, outputs: grade_mri_reconstruction(
                inputs,
                inputs.parent / "evaluator",
                outputs,
            ),
        ),
    )
    runs: list[dict[str, object]] = []
    for condition in CONDITIONS:
        for task_id, create_fixture, solve, grade in task_definitions:
            run_id = f"smoke-{condition.name}-{task_id.lower()}"
            run_directory = output_root / run_id
            inputs = run_directory / "inputs"
            outputs = run_directory / "outputs"
            run_directory.mkdir(parents=True, exist_ok=False)
            create_fixture(inputs)
            machine = AgentStateMachine()
            ledger = BudgetLedger(BudgetSpec(tool_calls=1, wall_time_ms=60_000))
            trajectory_path = run_directory / "trajectory.jsonl"
            with TrajectoryWriter(trajectory_path) as writer:
                sequence = 0
                if condition.planning:
                    sequence = _transition(
                        writer, sequence, run_id, task_id, machine, AgentPhase.PLANNING, ledger
                    )
                    sequence = _transition(
                        writer, sequence, run_id, task_id, machine, AgentPhase.EXECUTING, ledger
                    )
                else:
                    sequence = _transition(
                        writer, sequence, run_id, task_id, machine, AgentPhase.EXECUTING, ledger
                    )
                reservation = ledger.reserve(BudgetUsage(tool_calls=1, wall_time_ms=60_000))
                solve(inputs, outputs)
                ledger.reconcile(reservation, BudgetUsage(tool_calls=1))
                sequence = _transition(
                    writer, sequence, run_id, task_id, machine, AgentPhase.FINALIZING, ledger
                )
                report = grade(inputs, outputs)
                final_phase = AgentPhase.SUCCEEDED if report.success else AgentPhase.FAILED
                artifact_hashes = {
                    path.name: sha256_file(path)
                    for path in sorted(outputs.iterdir())
                    if path.is_file()
                }
                _transition(
                    writer,
                    sequence,
                    run_id,
                    task_id,
                    machine,
                    final_phase,
                    ledger,
                    {"grade": report.to_dict(), "artifact_hashes": artifact_hashes},
                )
            runs.append(
                {
                    "run_id": run_id,
                    "condition": condition.name,
                    "task_id": task_id,
                    "success": report.success,
                    "tool_calls": ledger.committed.tool_calls,
                }
            )

    summary: dict[str, object] = {
        "suite": "a1-smoke-v1",
        "policy": "scripted_reference",
        "research_result": False,
        "runs": runs,
        "successes": sum(bool(run["success"]) for run in runs),
        "total_runs": len(runs),
    }
    (output_root / "metrics.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def _transition(
    writer: TrajectoryWriter,
    sequence: int,
    run_id: str,
    task_id: str,
    machine: AgentStateMachine,
    target: AgentPhase,
    ledger: BudgetLedger,
    payload: dict[str, object] | None = None,
) -> int:
    before, after = machine.transition(target)
    writer.append(
        TrajectoryEvent(
            sequence=sequence,
            timestamp_utc=datetime.now(UTC).isoformat(),
            run_id=run_id,
            task_id=task_id,
            event_type="state_transition",
            state_before=before,
            state_after=after,
            budget=ledger.committed,
            payload=payload or {},
        )
    )
    return sequence + 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    summary = run_smoke(arguments.output)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
