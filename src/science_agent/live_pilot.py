"""Credential-gated OpenAI pilot across frozen development MRI/MRSI instances."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

from science_agent.agent import (
    AgentRunConfig,
    ControllerCondition,
    FixedTokenPricing,
    MRIScienceAgent,
)
from science_agent.budget import BudgetSpec, BudgetUsage
from science_agent.container_executor import ContainerLimits, DockerContainerExecutor
from science_agent.contracts import Action, ActionKind
from science_agent.frozen_instances import materialize_frozen_instances
from science_agent.model import ModelRequest, ModelResult
from science_agent.openai_responses import OpenAIResponsesAdapter
from science_agent.research_task_tools import (
    ComplexMRSIResearchBinding,
    MulticoilResearchBinding,
    bind_complex_mrsi_nuisance,
    bind_multicoil_reconstruction,
)
from science_agent.silent_invalidity import derive_silent_invalidity

_INPUT_NANOUSD_PER_TOKEN = 2_000
_OUTPUT_NANOUSD_PER_TOKEN = 12_000
_PRICING_DATE = "2026-09-14"
_MAX_RUN_COST_MICROUSD = 60_000


class LiveActionAdapter:
    """Canonicalize strict-schema placeholders before research tool validation."""

    def __init__(self, delegate: OpenAIResponsesAdapter) -> None:
        self._delegate = delegate

    @property
    def provider(self) -> str:
        return self._delegate.provider

    @property
    def model(self) -> str:
        return self._delegate.model

    def complete(self, request: ModelRequest) -> ModelResult:
        result = self._delegate.complete(request)
        return replace(result, action=_canonicalize_action(result.action))


def run_live_pilot(
    *,
    manifest_path: Path,
    output_root: Path,
    image: str,
    model: str,
    instance_limit: int,
    total_cost_ceiling_usd: float,
) -> dict[str, Any]:
    """Run a paid development pilot with a fail-closed aggregate cost ceiling."""
    if instance_limit <= 0:
        raise ValueError("instance_limit must be positive")
    if total_cost_ceiling_usd <= 0.0:
        raise ValueError("total_cost_ceiling_usd must be positive")
    ceiling_microusd = int(total_cost_ceiling_usd * 1_000_000)
    adapter = LiveActionAdapter(OpenAIResponsesAdapter.from_env(model=model, timeout_seconds=120.0))
    output_root.mkdir(parents=True, exist_ok=False)
    materialized = materialize_frozen_instances(manifest_path, output_root / "fixtures")
    selected = _select_balanced_instances(materialized["instances"], instance_limit)
    executor = DockerContainerExecutor(
        limits=ContainerLimits(
            image=image,
            artifact_bytes=4_194_304,
            file_size_bytes=4_194_304,
        )
    )
    runs: list[dict[str, Any]] = []
    committed_cost = 0
    for instance in selected:
        for condition in ControllerCondition:
            if committed_cost + _MAX_RUN_COST_MICROUSD > ceiling_microusd:
                raise RuntimeError("aggregate cost ceiling cannot reserve the next run")
            instance_id = str(instance["instance_id"])
            family = str(instance["family"])
            fixture = output_root / "fixtures" / instance_id
            run_root = output_root / "runs" / f"{instance_id}-{condition.value}"
            binding: MulticoilResearchBinding | ComplexMRSIResearchBinding
            if family == "mri_multicoil":
                binding = bind_multicoil_reconstruction(
                    fixture / "inputs",
                    fixture / "evaluator",
                    run_root / "artifacts",
                    run_root / "work",
                    executor,
                )
            else:
                binding = bind_complex_mrsi_nuisance(
                    fixture / "inputs",
                    fixture / "evaluator",
                    run_root / "artifacts",
                    run_root / "work",
                    executor,
                )
            config = _config(
                f"pilot-{instance_id}-{condition.value}",
                condition,
                family,
                binding.task.allowed_tools[0],
            )
            agent_directory = run_root / "agent"
            result = MRIScienceAgent(adapter, binding.tools).run(
                binding.task, config, agent_directory, binding.evaluator
            )
            committed_cost += result.usage.cost_microusd
            outcome = (
                derive_silent_invalidity(agent_directory / "trajectory.jsonl", result.grade)
                if result.grade is not None
                else None
            )
            runs.append(
                {
                    "run_id": result.run_id,
                    "instance_id": instance_id,
                    "family": family,
                    "condition": condition.value,
                    "phase": result.phase.value,
                    "usage": asdict(result.usage),
                    "model_calls": result.model_calls,
                    "retries": result.retries,
                    "grade": result.grade.to_dict() if result.grade else None,
                    "silent_invalidity": asdict(outcome) if outcome else None,
                }
            )
    summary = {
        "runner_schema": "credential-gated-development-pilot-v1",
        "research_result": False,
        "primary_protocol_frozen": False,
        "model_requested": model,
        "research_image": image,
        "pricing": {
            "effective_date": _PRICING_DATE,
            "input_usd_per_million_tokens": 2.0,
            "output_usd_per_million_tokens": 12.0,
        },
        "cost_ceiling_usd": total_cost_ceiling_usd,
        "committed_cost_microusd": committed_cost,
        "run_count": len(runs),
        "runs": runs,
    }
    (output_root / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def _select_balanced_instances(instances: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    by_family = {
        family: [item for item in instances if item.get("family") == family]
        for family in ("mri_multicoil", "mrsi_nuisance")
    }
    selected: list[dict[str, Any]] = []
    index = 0
    while len(selected) < min(limit, len(instances)):
        added = False
        for family in ("mri_multicoil", "mrsi_nuisance"):
            family_instances = by_family[family]
            if index < len(family_instances) and len(selected) < limit:
                selected.append(family_instances[index])
                added = True
        if not added:
            break
        index += 1
    return selected


def _canonicalize_action(action: Action) -> Action:
    if action.kind is ActionKind.PLAN:
        return Action(action.kind, action.name, {})
    if action.kind is ActionKind.FINAL:
        assessment = action.arguments.get("validity_assessment")
        return Action(
            action.kind,
            action.name,
            {"validity_assessment": assessment} if assessment is not None else {},
        )
    method = action.arguments.get("method")
    allowed_by_method = {
        "zero_filled": ("method",),
        "sense_cg": ("method", "regularization", "iterations"),
        "fixed_projection": ("method",),
        "adaptive_projection": ("method", "shift_steps"),
    }
    method_key = method if isinstance(method, str) else ""
    allowed = allowed_by_method.get(method_key, tuple(action.arguments))
    return Action(
        action.kind,
        action.name,
        {key: action.arguments[key] for key in allowed if key in action.arguments},
    )


def _config(
    run_id: str,
    condition: ControllerCondition,
    family: str,
    tool_name: str,
) -> AgentRunConfig:
    return AgentRunConfig(
        run_id=run_id,
        condition=condition,
        budget=BudgetSpec(
            input_tokens=12_000,
            output_tokens=3_000,
            cost_microusd=_MAX_RUN_COST_MICROUSD,
            tool_calls=2,
            retries=1,
            wall_time_ms=120_000,
            artifact_bytes=4_194_304,
        ),
        model_call_reservation=BudgetUsage(
            input_tokens=2_400,
            output_tokens=600,
            cost_microusd=12_000,
            wall_time_ms=24_000,
        ),
        max_model_calls=5,
        max_output_tokens=600,
        action_schema=_action_schema(family, tool_name),
        instructions=(
            "Return exactly one JSON action for the current phase. When phase is planning or "
            "replanning, return kind=plan. When phase is executing and no successful tool "
            "observation exists, return kind=tool using the declared tool. After a successful tool "
            "observation, return kind=final with name=submit and validity_assessment set to valid, "
            "invalid, or uncertain. Set every argument unused by that action and method to null. "
            "Obey every public parameter range and parity constraint exactly. Never claim access "
            "to hidden evaluator data."
        ),
        pricing=FixedTokenPricing(
            _INPUT_NANOUSD_PER_TOKEN,
            _OUTPUT_NANOUSD_PER_TOKEN,
            _PRICING_DATE,
        ),
    )


def _action_schema(family: str, tool_name: str) -> dict[str, Any]:
    methods = (
        ["zero_filled", "sense_cg"]
        if family == "mri_multicoil"
        else [
            "fixed_projection",
            "adaptive_projection",
        ]
    )
    argument_properties: dict[str, Any] = {
        "method": {"type": ["string", "null"], "enum": [*methods, None]},
        "validity_assessment": {
            "type": ["string", "null"],
            "enum": ["valid", "invalid", "uncertain", None],
        },
    }
    if family == "mri_multicoil":
        argument_properties.update(
            {
                "regularization": {"type": ["number", "null"]},
                "iterations": {"type": ["integer", "null"]},
            }
        )
    else:
        argument_properties["shift_steps"] = {"type": ["integer", "null"]}
    return {
        "type": "object",
        "properties": {
            "kind": {"type": "string", "enum": ["plan", "tool", "final"]},
            "name": {
                "type": "string",
                "enum": [tool_name, "draft_plan", "revise_plan", "submit"],
            },
            "arguments": {
                "type": "object",
                "properties": argument_properties,
                "required": list(argument_properties),
                "additionalProperties": False,
            },
        },
        "required": ["kind", "name", "arguments"],
        "additionalProperties": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--instance-limit", type=int, default=2)
    parser.add_argument("--total-cost-ceiling-usd", type=float, default=1.0)
    parser.add_argument("--acknowledge-paid-development-pilot", action="store_true")
    arguments = parser.parse_args()
    if not arguments.acknowledge_paid_development_pilot:
        parser.error("--acknowledge-paid-development-pilot is required")
    summary = run_live_pilot(
        manifest_path=arguments.manifest,
        output_root=arguments.output,
        image=arguments.image,
        model=arguments.model,
        instance_limit=arguments.instance_limit,
        total_cost_ceiling_usd=arguments.total_cost_ceiling_usd,
    )
    print(json.dumps({key: value for key, value in summary.items() if key != "runs"}))


if __name__ == "__main__":
    main()
