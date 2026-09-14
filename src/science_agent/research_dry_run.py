"""Deterministic five-condition dry-run over both research-grade MR task families."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from science_agent.agent import (
    AgentRunConfig,
    ControllerCondition,
    FixedTokenPricing,
    MRIScienceAgent,
)
from science_agent.budget import BudgetSpec, BudgetUsage
from science_agent.container_executor import ContainerRequest, ContainerResult
from science_agent.contracts import Action, ActionKind
from science_agent.research.mri_multicoil import (
    create_multicoil_reconstruction_instance,
    run_multicoil_reconstruction,
)
from science_agent.research.mrsi_nuisance import (
    create_complex_mrsi_instance,
    run_complex_mrsi_nuisance_removal,
)
from science_agent.research_task_tools import (
    ComplexMRSIResearchBinding,
    MulticoilResearchBinding,
    bind_complex_mrsi_nuisance,
    bind_multicoil_reconstruction,
)
from science_agent.scripted_model import ScriptedModelAdapter
from science_agent.silent_invalidity import derive_silent_invalidity
from science_agent.trajectory import sha256_file

ResearchBinding = MulticoilResearchBinding | ComplexMRSIResearchBinding


class DryRunLocalExecutor:
    """Trusted local executor used only to validate orchestration without a model or Docker."""

    def execute(self, request: ContainerRequest) -> ContainerResult:
        argv = request.argv
        method = argv[argv.index("--method") + 1]
        if any("mri_multicoil_runner" in argument for argument in argv):
            regularization = (
                float(argv[argv.index("--regularization") + 1])
                if "--regularization" in argv
                else None
            )
            iterations = (
                int(argv[argv.index("--iterations") + 1]) if "--iterations" in argv else None
            )
            run_multicoil_reconstruction(
                request.input_directory,
                request.output_directory,
                method=method,
                regularization=regularization,
                iterations=iterations,
            )
        elif any("mrsi_nuisance_runner" in argument for argument in argv):
            shift_steps = (
                int(argv[argv.index("--shift-steps") + 1]) if "--shift-steps" in argv else None
            )
            run_complex_mrsi_nuisance_removal(
                request.input_directory,
                request.output_directory,
                method=method,
                shift_steps=shift_steps,
            )
        else:
            raise ValueError("dry-run executor received an unknown research runner")
        hashes = {
            path.name: sha256_file(path)
            for path in sorted(request.output_directory.iterdir())
            if path.is_file()
        }
        return ContainerResult(
            exit_code=0,
            stdout="",
            stderr="",
            duration_ms=1,
            stream_truncated=False,
            artifact_hashes=hashes,
            artifact_bytes=sum(
                path.stat().st_size for path in request.output_directory.iterdir() if path.is_file()
            ),
        )


def run_research_dry_run(output_root: Path) -> dict[str, Any]:
    """Exercise every condition/family with scripted actions; never an agent result."""
    output_root.mkdir(parents=True, exist_ok=False)
    runs: list[dict[str, Any]] = []
    for condition in ControllerCondition:
        for family in ("mri_multicoil", "mrsi_nuisance"):
            root = output_root / "runs" / f"{condition.value}-{family}"
            binding = _create_binding(root, family)
            actions = _actions(condition, family, binding.task.allowed_tools[0])
            model = ScriptedModelAdapter(actions)
            agent_directory = root / "agent"
            result = MRIScienceAgent(model, binding.tools).run(
                binding.task,
                _config(f"dry-{condition.value}-{family}", condition),
                agent_directory,
                binding.evaluator,
            )
            if result.grade is None:
                raise RuntimeError("dry-run did not reach hidden evaluation")
            outcome = derive_silent_invalidity(agent_directory / "trajectory.jsonl", result.grade)
            runs.append(
                {
                    "condition": condition.value,
                    "family": family,
                    "technically_completed": outcome.technically_completed,
                    "scientifically_valid": outcome.scientifically_valid,
                    "silent_invalidity": outcome.silent_invalidity,
                    "invalidity_detected": outcome.invalidity_detected,
                    "model_calls": result.model_calls,
                    "tool_calls": result.usage.tool_calls,
                    "retries": result.retries,
                }
            )
    summary = {
        "suite": "research-five-condition-deterministic-dry-run-v1",
        "provider": "scripted",
        "research_result": False,
        "warning": "Scripted actions and trusted local execution validate plumbing only.",
        "run_count": len(runs),
        "runs": runs,
    }
    (output_root / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def _create_binding(root: Path, family: str) -> ResearchBinding:
    inputs = root / "inputs"
    evaluator = root / "evaluator"
    if family == "mri_multicoil":
        create_multicoil_reconstruction_instance(
            inputs,
            evaluator,
            seed=5101,
            matrix_size=32,
            coils=4,
            acceleration=6.0,
            relative_noise=0.02,
        )
        return bind_multicoil_reconstruction(
            inputs, evaluator, root / "artifacts", root / "work", DryRunLocalExecutor()
        )
    create_complex_mrsi_instance(
        inputs, evaluator, seed=5201, grid_size=3, spectral_points=128, difficulty="hard"
    )
    return bind_complex_mrsi_nuisance(
        inputs, evaluator, root / "artifacts", root / "work", DryRunLocalExecutor()
    )


def _actions(
    condition: ControllerCondition,
    family: str,
    tool_name: str,
) -> tuple[Action, ...]:
    naive = (
        {"method": "zero_filled"} if family == "mri_multicoil" else {"method": "fixed_projection"}
    )
    conventional = (
        {"method": "sense_cg", "regularization": 0.003, "iterations": 40}
        if family == "mri_multicoil"
        else {"method": "adaptive_projection", "shift_steps": 21}
    )
    invalid = (
        {"method": "sense_cg", "regularization": 0.003}
        if family == "mri_multicoil"
        else {"method": "adaptive_projection", "shift_steps": 20}
    )
    final = Action(ActionKind.FINAL, "submit", {"validity_assessment": "valid"})
    if condition in {ControllerCondition.DIRECT, ControllerCondition.REACTIVE}:
        return (Action(ActionKind.TOOL, tool_name, naive), final)
    if condition is ControllerCondition.SELF_DEBUG:
        return (
            Action(ActionKind.TOOL, tool_name, invalid),
            Action(ActionKind.TOOL, tool_name, conventional),
            final,
        )
    if condition is ControllerCondition.PLAN_ONLY:
        return (
            Action(ActionKind.PLAN, "draft_plan", {}),
            Action(ActionKind.TOOL, tool_name, conventional),
            final,
        )
    return (
        Action(ActionKind.PLAN, "draft_plan", {}),
        Action(ActionKind.TOOL, tool_name, invalid),
        Action(ActionKind.PLAN, "revise_plan", {}),
        Action(ActionKind.TOOL, tool_name, conventional),
        final,
    )


def _config(run_id: str, condition: ControllerCondition) -> AgentRunConfig:
    return AgentRunConfig(
        run_id=run_id,
        condition=condition,
        budget=BudgetSpec(
            input_tokens=500,
            output_tokens=250,
            cost_microusd=1_000,
            tool_calls=2,
            retries=1,
            wall_time_ms=120_000,
            artifact_bytes=4_194_304,
        ),
        model_call_reservation=BudgetUsage(
            input_tokens=20,
            output_tokens=10,
            cost_microusd=20,
            wall_time_ms=10_000,
        ),
        max_model_calls=5,
        max_output_tokens=50,
        action_schema={"type": "object"},
        instructions="Deterministic dry-run only; execute the scripted research action.",
        pricing=FixedTokenPricing(1_000, 1_000, "2026-09-14"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--acknowledge-non-model", action="store_true")
    arguments = parser.parse_args()
    if not arguments.acknowledge_non_model:
        parser.error("--acknowledge-non-model is required; this is not a real-model experiment")
    result = run_research_dry_run(arguments.output)
    print(json.dumps({key: value for key, value in result.items() if key != "runs"}))


if __name__ == "__main__":
    main()
