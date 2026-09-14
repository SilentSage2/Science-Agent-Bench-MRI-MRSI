"""Offline end-to-end MRI/MRSI agent smoke using development reference tools."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path

from science_agent.agent import (
    AgentRunConfig,
    ControllerCondition,
    FixedTokenPricing,
    MRIScienceAgent,
)
from science_agent.budget import BudgetSpec, BudgetUsage
from science_agent.contracts import Action, ActionKind
from science_agent.scripted_model import ScriptedModelAdapter
from science_agent.task_tools import (
    ReferenceTaskBinding,
    bind_mri_leakage_reference,
    bind_mri_reconstruction_reference,
    bind_mrs_fit_reference,
    bind_mrsi_nuisance_reference,
)
from science_agent.tasks import (
    create_mri_leakage_fixture,
    create_mri_reconstruction_fixture,
    create_mrs_fit_fixture,
    create_mrsi_nuisance_fixture,
)

BindingFactory = Callable[[Path], ReferenceTaskBinding]

_ACTION_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": ["plan", "tool", "final"]},
        "name": {"type": "string"},
        "arguments": {"type": "object", "additionalProperties": False},
    },
    "required": ["kind", "name", "arguments"],
    "additionalProperties": False,
}


def run_agent_smoke(output_root: Path) -> dict[str, object]:
    """Run every implemented family through the real agent orchestration path."""
    output_root.mkdir(parents=True, exist_ok=False)
    definitions = _create_fixtures(output_root / "fixtures")
    runs: list[dict[str, object]] = []
    for condition in ControllerCondition:
        for task_label, make_binding in definitions:
            run_id = f"agent-smoke-{condition.value}-{task_label}"
            run_directory = output_root / "runs" / run_id
            binding = make_binding(run_directory / "artifacts")
            model = ScriptedModelAdapter(_actions(condition, binding.task.allowed_tools[0]))
            result = MRIScienceAgent(model, binding.tools).run(
                binding.task,
                _config(run_id, condition),
                run_directory,
                binding.evaluator,
            )
            runs.append(
                {
                    "run_id": run_id,
                    "condition": condition.value,
                    "task_id": binding.task.task_id,
                    "phase": result.phase.value,
                    "success": result.grade.success if result.grade else False,
                    "model_calls": result.model_calls,
                    "tool_calls": result.usage.tool_calls,
                }
            )
    summary: dict[str, object] = {
        "suite": "a1-agent-smoke-v1",
        "model": "scripted-reference-v1",
        "research_result": False,
        "runs": runs,
        "successes": sum(bool(run["success"]) for run in runs),
        "total_runs": len(runs),
    }
    (output_root / "metrics.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def _create_fixtures(root: Path) -> tuple[tuple[str, BindingFactory], ...]:
    mrs_inputs = root / "mrs-fit" / "inputs"
    create_mrs_fit_fixture(mrs_inputs, seed=1701)

    leakage_inputs = root / "mri-leakage" / "inputs"
    create_mri_leakage_fixture(leakage_inputs, seed=2301, include_violations=True)

    reconstruction_inputs = root / "mri-reconstruction" / "inputs"
    reconstruction_evaluator = root / "mri-reconstruction" / "evaluator"
    create_mri_reconstruction_fixture(
        reconstruction_inputs,
        reconstruction_evaluator,
        seed=3101,
        matrix_size=8,
    )

    nuisance_inputs = root / "mrsi-nuisance" / "inputs"
    nuisance_evaluator = root / "mrsi-nuisance" / "evaluator"
    create_mrsi_nuisance_fixture(
        nuisance_inputs,
        nuisance_evaluator,
        seed=4101,
        grid_size=2,
    )

    return (
        ("mrs-fit", lambda output: bind_mrs_fit_reference(mrs_inputs, output)),
        (
            "mri-leakage",
            lambda output: bind_mri_leakage_reference(leakage_inputs, output),
        ),
        (
            "mri-reconstruction",
            lambda output: bind_mri_reconstruction_reference(
                reconstruction_inputs, reconstruction_evaluator, output
            ),
        ),
        (
            "mrsi-nuisance",
            lambda output: bind_mrsi_nuisance_reference(
                nuisance_inputs, nuisance_evaluator, output
            ),
        ),
    )


def _actions(condition: ControllerCondition, tool_name: str) -> tuple[Action, ...]:
    actions = [Action(ActionKind.TOOL, tool_name, {}), Action(ActionKind.FINAL, "submit", {})]
    if condition.planning:
        actions.insert(0, Action(ActionKind.PLAN, "draft_plan", {}))
    return tuple(actions)


def _config(run_id: str, condition: ControllerCondition) -> AgentRunConfig:
    return AgentRunConfig(
        run_id=run_id,
        condition=condition,
        budget=BudgetSpec(
            input_tokens=100,
            output_tokens=100,
            cost_microusd=100,
            tool_calls=1,
            retries=1,
            wall_time_ms=70_000,
            artifact_bytes=1_048_576,
        ),
        model_call_reservation=BudgetUsage(
            input_tokens=20,
            output_tokens=10,
            cost_microusd=20,
            wall_time_ms=1_000,
        ),
        max_model_calls=3,
        max_output_tokens=10,
        action_schema=_ACTION_SCHEMA,
        instructions="Return one action for the declared MRI/MRSI task and controller phase.",
        pricing=FixedTokenPricing(1_000, 1_000, "2026-09-14"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(run_agent_smoke(arguments.output), sort_keys=True))


if __name__ == "__main__":
    main()
