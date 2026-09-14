from __future__ import annotations

import json
import tempfile
import unittest
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from science_agent.agent import (
    AgentRunConfig,
    ControllerCondition,
    FixedTokenPricing,
    MRIScienceAgent,
)
from science_agent.budget import BudgetSpec, BudgetUsage
from science_agent.contracts import Action, ActionKind, Observation, TaskSpec
from science_agent.grading import GradeReport
from science_agent.model import ModelRequest, ModelResult, ModelUsage
from science_agent.state import AgentPhase
from science_agent.tools import RegisteredTool, ToolRegistry, ToolResult


class ScriptedModel:
    def __init__(self, actions: list[Action], usage: ModelUsage | None = None) -> None:
        self._actions = iter(actions)
        self._usage = usage or ModelUsage(input_tokens=10, output_tokens=5)
        self.requests: list[ModelRequest] = []

    @property
    def provider(self) -> str:
        return "scripted"

    @property
    def model(self) -> str:
        return "scripted-v1"

    def complete(self, request: ModelRequest) -> ModelResult:
        self.requests.append(request)
        return ModelResult(
            provider=self.provider,
            model=self.model,
            response_id=f"response-{len(self.requests)}",
            action=next(self._actions),
            usage=self._usage,
        )


class ObservationQueue:
    def __init__(self, observations: list[Observation]) -> None:
        self._observations = iter(observations)
        self.calls = 0

    def __call__(self, _: Mapping[str, Any]) -> ToolResult:
        self.calls += 1
        return ToolResult(next(self._observations), BudgetUsage(tool_calls=1, wall_time_ms=1))


def _task() -> TaskSpec:
    return TaskSpec(
        task_id="SAB-MRI-TEST-001",
        schema_version="1",
        objective="Produce a deterministic MRI research artifact.",
        allowed_tools=("analyze_mri",),
        required_artifacts=("result.json",),
    )


def _config(run_id: str, condition: ControllerCondition, retries: int = 1) -> AgentRunConfig:
    return AgentRunConfig(
        run_id=run_id,
        condition=condition,
        budget=BudgetSpec(
            input_tokens=100,
            output_tokens=100,
            cost_microusd=100,
            tool_calls=2,
            retries=retries,
            wall_time_ms=10_000,
        ),
        model_call_reservation=BudgetUsage(
            input_tokens=20,
            output_tokens=10,
            cost_microusd=20,
            wall_time_ms=1_000,
        ),
        max_model_calls=5,
        max_output_tokens=10,
        action_schema={
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": ["plan", "tool", "final"]},
                "name": {"type": "string"},
                "arguments": {"type": "object"},
            },
        },
        instructions="Return exactly one valid action.",
        pricing=FixedTokenPricing(1_000, 1_000, "2026-09-14"),
    )


def _passing_grade() -> GradeReport:
    return GradeReport(True, True, True, True)


def _tool_action() -> Action:
    return Action(ActionKind.TOOL, "analyze_mri", {"mode": "deterministic"})


def _plan_action(name: str = "plan") -> Action:
    return Action(ActionKind.PLAN, name, {})


def _final_action() -> Action:
    return Action(ActionKind.FINAL, "submit", {})


class MRIScienceAgentTests(unittest.TestCase):
    def _run(
        self,
        model: ScriptedModel,
        tool: ObservationQueue,
        condition: ControllerCondition,
        *,
        retries: int = 1,
    ) -> tuple[Any, list[dict[str, Any]]]:
        registry = ToolRegistry(
            (
                RegisteredTool(
                    "analyze_mri",
                    BudgetUsage(tool_calls=1, wall_time_ms=10),
                    tool,
                ),
            )
        )
        with tempfile.TemporaryDirectory() as temporary:
            run_directory = Path(temporary) / "run"
            result = MRIScienceAgent(model, registry).run(
                _task(), _config("run-1", condition, retries), run_directory, _passing_grade
            )
            events = [
                json.loads(line)
                for line in (run_directory / "trajectory.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            manifest = json.loads((run_directory / "run_manifest.json").read_text(encoding="utf-8"))
            self.assertNotIn("api_key", manifest)
            self.assertEqual(manifest["condition"], condition.value)
        return result, events

    def test_reactive_tool_then_final_succeeds(self) -> None:
        model = ScriptedModel([_tool_action(), _final_action()])
        tool = ObservationQueue([Observation(True, "ok")])

        result, events = self._run(model, tool, ControllerCondition.REACTIVE)

        self.assertEqual(result.phase, AgentPhase.SUCCEEDED)
        self.assertEqual(result.model_calls, 2)
        self.assertEqual(result.usage.tool_calls, 1)
        self.assertEqual(tool.calls, 1)
        self.assertEqual(events[-1]["state_after"], "succeeded")

    def test_direct_uses_nonplanning_path(self) -> None:
        model = ScriptedModel(
            [
                Action(
                    ActionKind.TOOL,
                    "analyze_mri",
                    {"mode": "deterministic", "validity_assessment": "valid"},
                )
            ]
        )
        tool = ObservationQueue([Observation(True, "ok")])

        result, events = self._run(model, tool, ControllerCondition.DIRECT)

        self.assertEqual(result.phase, AgentPhase.SUCCEEDED)
        transitions = [
            event["state_after"] for event in events if event["event_type"] == "state_transition"
        ]
        self.assertNotIn("planning", transitions)
        self.assertEqual(result.model_calls, 1)
        self.assertEqual(len(model.requests), 1)
        self.assertEqual(tool.calls, 1)

    def test_self_debug_revises_a_successful_candidate_once(self) -> None:
        model = ScriptedModel(
            [
                Action(ActionKind.TOOL, "analyze_mri", {"mode": "initial"}),
                Action(ActionKind.TOOL, "analyze_mri", {"mode": "revised"}),
                _final_action(),
            ]
        )
        tool = ObservationQueue(
            [
                Observation(True, "public_diagnostic_suspicious", {"residual": 0.4}),
                Observation(True, "public_diagnostic_improved", {"residual": 0.1}),
            ]
        )

        result, events = self._run(model, tool, ControllerCondition.SELF_DEBUG)

        self.assertEqual(result.phase, AgentPhase.SUCCEEDED)
        self.assertEqual(result.retries, 1)
        self.assertEqual(result.usage.retries, 1)
        self.assertEqual(tool.calls, 2)
        transitions = [
            event["state_after"] for event in events if event["event_type"] == "state_transition"
        ]
        self.assertIn("reviewing", transitions)
        kinds = [request.output_schema["properties"]["kind"]["enum"] for request in model.requests]
        self.assertEqual(kinds, [["tool"], ["tool"], ["final"]])

    def test_self_debug_rejects_an_unchanged_successful_candidate(self) -> None:
        model = ScriptedModel([_tool_action(), _tool_action()])
        tool = ObservationQueue([Observation(True, "public_diagnostic_suspicious")])

        result, events = self._run(model, tool, ControllerCondition.SELF_DEBUG)

        self.assertEqual(result.phase, AgentPhase.FAILED)
        self.assertEqual(
            events[-1]["payload"]["reason"], "scientific_revision_must_change_candidate"
        )
        self.assertEqual(tool.calls, 1)

    def test_self_debug_cannot_skip_successful_candidate_revision(self) -> None:
        model = ScriptedModel([_tool_action(), _final_action()])
        tool = ObservationQueue([Observation(True, "public_diagnostic_suspicious")])

        result, events = self._run(model, tool, ControllerCondition.SELF_DEBUG)

        self.assertEqual(result.phase, AgentPhase.FAILED)
        self.assertEqual(events[-1]["payload"]["reason"], "scientific_revision_required")
        self.assertEqual(tool.calls, 1)

    def test_direct_requires_pre_observation_validity_commitment(self) -> None:
        model = ScriptedModel([_tool_action()])
        tool = ObservationQueue([Observation(True, "ok")])

        result, events = self._run(model, tool, ControllerCondition.DIRECT)

        self.assertEqual(result.phase, AgentPhase.POLICY_VIOLATION)
        self.assertEqual(events[-1]["payload"]["reason"], "direct_validity_precommit_required")
        self.assertEqual(tool.calls, 0)

    def test_self_debug_retries_without_structured_replan(self) -> None:
        model = ScriptedModel([_tool_action(), _tool_action(), _final_action()])
        tool = ObservationQueue(
            [Observation(False, "retryable_check", retryable=True), Observation(True, "ok")]
        )

        result, events = self._run(model, tool, ControllerCondition.SELF_DEBUG)

        self.assertEqual(result.phase, AgentPhase.SUCCEEDED)
        self.assertEqual(result.retries, 1)
        transitions = [
            event["state_after"] for event in events if event["event_type"] == "state_transition"
        ]
        self.assertIn("retrying", transitions)
        self.assertNotIn("replanning", transitions)

    def test_plan_only_requires_plan_and_does_not_retry(self) -> None:
        model = ScriptedModel([_plan_action(), _tool_action()])
        tool = ObservationQueue([Observation(False, "fit_failed", retryable=True)])

        result, _ = self._run(model, tool, ControllerCondition.PLAN_ONLY)

        self.assertEqual(result.phase, AgentPhase.FAILED)
        self.assertEqual(result.retries, 0)
        self.assertEqual(tool.calls, 1)

    def test_model_request_schema_is_narrowed_by_phase(self) -> None:
        model = ScriptedModel([_plan_action(), _tool_action(), _final_action()])
        tool = ObservationQueue([Observation(True, "ok")])

        result, _ = self._run(model, tool, ControllerCondition.PLAN_ONLY)

        self.assertEqual(result.phase, AgentPhase.SUCCEEDED)
        kinds = [request.output_schema["properties"]["kind"]["enum"] for request in model.requests]
        names = [request.output_schema["properties"]["name"]["enum"] for request in model.requests]
        self.assertEqual(kinds, [["plan"], ["tool"], ["final"]])
        self.assertEqual(names[0], ["draft_plan"])
        self.assertEqual(names[1], ["analyze_mri"])
        self.assertEqual(names[2], ["submit"])

    def test_plan_condition_fails_cleanly_when_initial_action_is_not_plan(self) -> None:
        model = ScriptedModel([_tool_action()])
        tool = ObservationQueue([Observation(True, "ok")])

        result, events = self._run(model, tool, ControllerCondition.PLAN_ONLY)

        self.assertEqual(result.phase, AgentPhase.FAILED)
        self.assertEqual(tool.calls, 0)
        self.assertEqual(events[-1]["payload"]["reason"], "initial_plan_required")

    def test_retry_condition_replans_once_and_recovers(self) -> None:
        model = ScriptedModel(
            [
                _plan_action(),
                _tool_action(),
                _plan_action("replan"),
                _tool_action(),
                _final_action(),
            ]
        )
        tool = ObservationQueue(
            [Observation(False, "temporary_failure", retryable=True), Observation(True, "ok")]
        )

        result, events = self._run(model, tool, ControllerCondition.PLAN_RETRY_REPLAN)

        self.assertEqual(result.phase, AgentPhase.SUCCEEDED)
        self.assertEqual(result.retries, 1)
        self.assertEqual(result.usage.retries, 1)
        self.assertEqual(tool.calls, 2)
        transitions = [
            event["state_after"] for event in events if event["event_type"] == "state_transition"
        ]
        self.assertIn("retrying", transitions)
        self.assertIn("replanning", transitions)

    def test_retry_condition_requires_structured_replan(self) -> None:
        model = ScriptedModel([_plan_action(), _tool_action(), _final_action()])
        tool = ObservationQueue([Observation(False, "temporary_failure", retryable=True)])

        result, events = self._run(model, tool, ControllerCondition.PLAN_RETRY_REPLAN)

        self.assertEqual(result.phase, AgentPhase.FAILED)
        self.assertEqual(events[-1]["payload"]["reason"], "replan_required")

    def test_disallowed_tool_is_policy_violation_without_execution(self) -> None:
        model = ScriptedModel([Action(ActionKind.TOOL, "shell", {})])
        tool = ObservationQueue([Observation(True, "ok")])

        result, _ = self._run(model, tool, ControllerCondition.REACTIVE)

        self.assertEqual(result.phase, AgentPhase.POLICY_VIOLATION)
        self.assertEqual(tool.calls, 0)

    def test_missing_provider_usage_fails_closed(self) -> None:
        model = ScriptedModel([_tool_action()], ModelUsage(input_tokens=None, output_tokens=None))
        tool = ObservationQueue([Observation(True, "ok")])

        result, _ = self._run(model, tool, ControllerCondition.REACTIVE)

        self.assertEqual(result.phase, AgentPhase.FAILED)
        self.assertEqual(result.usage.input_tokens, 0)
        self.assertEqual(tool.calls, 0)

    def test_model_usage_above_reservation_is_budget_exceeded(self) -> None:
        model = ScriptedModel([_tool_action()], ModelUsage(input_tokens=21, output_tokens=5))
        tool = ObservationQueue([Observation(True, "ok")])

        result, _ = self._run(model, tool, ControllerCondition.REACTIVE)

        self.assertEqual(result.phase, AgentPhase.BUDGET_EXCEEDED)
        self.assertEqual(tool.calls, 0)

    def test_retry_budget_exhaustion_fails_before_replan(self) -> None:
        model = ScriptedModel([_plan_action(), _tool_action()])
        tool = ObservationQueue([Observation(False, "temporary_failure", retryable=True)])

        result, _ = self._run(model, tool, ControllerCondition.PLAN_RETRY_REPLAN, retries=0)

        self.assertEqual(result.phase, AgentPhase.BUDGET_EXCEEDED)
        self.assertEqual(len(model.requests), 2)


if __name__ == "__main__":
    unittest.main()
