"""Budget-controlled single-agent orchestration for the frozen A1 conditions."""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from science_agent.budget import (
    BudgetError,
    BudgetExceeded,
    BudgetLedger,
    BudgetSpec,
    BudgetUsage,
)
from science_agent.contracts import Action, ActionKind, Observation, TaskSpec
from science_agent.grading import GradeReport
from science_agent.model import ModelAdapter, ModelError, ModelRequest, ModelUsage
from science_agent.state import AgentPhase, AgentStateMachine
from science_agent.tools import ToolRegistry, ToolRegistryError, ToolResult
from science_agent.trajectory import TrajectoryEvent, TrajectoryWriter


class ControllerCondition(StrEnum):
    DIRECT = "direct"
    SELF_DEBUG = "self_debug"
    REACTIVE = "reactive"
    PLAN_ONLY = "plan_only"
    PLAN_RETRY_REPLAN = "plan_retry_replan"

    @property
    def planning(self) -> bool:
        return self in {
            ControllerCondition.PLAN_ONLY,
            ControllerCondition.PLAN_RETRY_REPLAN,
        }

    @property
    def retry(self) -> bool:
        return self in {
            ControllerCondition.SELF_DEBUG,
            ControllerCondition.PLAN_RETRY_REPLAN,
        }

    @property
    def replan_on_retry(self) -> bool:
        return self is ControllerCondition.PLAN_RETRY_REPLAN

    @property
    def observation_conditioned_final(self) -> bool:
        """Whether validity may be assessed after observing tool output."""
        return self is not ControllerCondition.DIRECT

    @property
    def successful_candidate_revision(self) -> bool:
        """Whether one clean successful candidate must be scientifically revised."""
        return self is ControllerCondition.SELF_DEBUG


class AgentRunError(ValueError):
    """Raised before a run when its frozen configuration is invalid."""


@dataclass(frozen=True, slots=True)
class FixedTokenPricing:
    """Frozen token prices in nanodollars/token, rounded up to microdollars."""

    input_nanousd_per_token: int
    output_nanousd_per_token: int
    effective_date: str

    def __post_init__(self) -> None:
        prices = (self.input_nanousd_per_token, self.output_nanousd_per_token)
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in prices
        ):
            raise AgentRunError("token prices must be non-negative")
        try:
            date.fromisoformat(self.effective_date)
        except (TypeError, ValueError) as exc:
            raise AgentRunError("pricing effective_date must be ISO YYYY-MM-DD") from exc

    def cost_microusd(self, usage: ModelUsage) -> int:
        if not usage.complete:
            raise AgentRunError("complete provider token usage is required")
        assert usage.input_tokens is not None
        assert usage.output_tokens is not None
        nanousd = (
            usage.input_tokens * self.input_nanousd_per_token
            + usage.output_tokens * self.output_nanousd_per_token
        )
        return (nanousd + 999) // 1000


@dataclass(frozen=True, slots=True)
class AgentRunConfig:
    run_id: str
    condition: ControllerCondition
    budget: BudgetSpec
    model_call_reservation: BudgetUsage
    max_model_calls: int
    max_output_tokens: int
    action_schema: Mapping[str, Any]
    instructions: str
    pricing: FixedTokenPricing

    def __post_init__(self) -> None:
        if not self.run_id.strip() or not self.instructions.strip():
            raise AgentRunError("run_id and instructions must not be empty")
        limits = (self.max_model_calls, self.max_output_tokens)
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in limits
        ):
            raise AgentRunError("model call and output-token limits must be positive")
        if not isinstance(self.action_schema, Mapping) or not self.action_schema:
            raise AgentRunError("action_schema must not be empty")


@dataclass(frozen=True, slots=True)
class AgentRunResult:
    run_id: str
    condition: ControllerCondition
    phase: AgentPhase
    usage: BudgetUsage
    model_calls: int
    retries: int
    grade: GradeReport | None


Evaluator = Callable[[], GradeReport]


class MRIScienceAgent:
    """One model, one controller, and an explicit MRI/MRSI tool boundary."""

    def __init__(self, model: ModelAdapter, tools: ToolRegistry) -> None:
        self._model = model
        self._tools = tools

    def run(
        self,
        task: TaskSpec,
        config: AgentRunConfig,
        run_directory: Path,
        evaluator: Evaluator,
    ) -> AgentRunResult:
        self._validate_tools(task)
        run_directory.mkdir(parents=True, exist_ok=False)
        _write_manifest(run_directory / "run_manifest.json", task, config, self._model)
        machine = AgentStateMachine()
        ledger = BudgetLedger(config.budget)
        history: list[dict[str, Any]] = []
        model_calls = 0
        retries = 0
        grade: GradeReport | None = None

        with TrajectoryWriter(run_directory / "trajectory.jsonl") as writer:
            sequence = 0
            if config.condition.planning:
                sequence = self._transition(
                    writer, sequence, config, task, machine, ledger, AgentPhase.PLANNING
                )
                action, sequence, model_calls = self._next_action(
                    writer,
                    sequence,
                    config,
                    task,
                    machine,
                    ledger,
                    history,
                    model_calls,
                )
                if action is None:
                    return self._result(config, machine, ledger, model_calls, retries, grade)
                if action.kind is not ActionKind.PLAN:
                    self._transition(
                        writer,
                        sequence,
                        config,
                        task,
                        machine,
                        ledger,
                        AgentPhase.FAILED,
                        {"reason": "initial_plan_required"},
                    )
                    return self._result(config, machine, ledger, model_calls, retries, grade)
                history.append(_action_record(action))
                sequence = self._transition(
                    writer, sequence, config, task, machine, ledger, AgentPhase.EXECUTING
                )
            else:
                sequence = self._transition(
                    writer, sequence, config, task, machine, ledger, AgentPhase.EXECUTING
                )

            while model_calls < config.max_model_calls and not machine.terminal:
                action, sequence, model_calls = self._next_action(
                    writer,
                    sequence,
                    config,
                    task,
                    machine,
                    ledger,
                    history,
                    model_calls,
                )
                if action is None:
                    break
                history.append(_action_record(action))

                if action.kind is ActionKind.FINAL:
                    if _scientific_revision_due(config.condition, history[:-1]):
                        self._transition(
                            writer,
                            sequence,
                            config,
                            task,
                            machine,
                            ledger,
                            AgentPhase.FAILED,
                            {"reason": "scientific_revision_required"},
                        )
                        break
                    sequence = self._transition(
                        writer,
                        sequence,
                        config,
                        task,
                        machine,
                        ledger,
                        AgentPhase.FINALIZING,
                    )
                    grade = evaluator()
                    final_phase = AgentPhase.SUCCEEDED if grade.success else AgentPhase.FAILED
                    self._transition(
                        writer,
                        sequence,
                        config,
                        task,
                        machine,
                        ledger,
                        final_phase,
                        {"grade": grade.to_dict()},
                    )
                    break

                if action.kind is not ActionKind.TOOL:
                    self._transition(
                        writer,
                        sequence,
                        config,
                        task,
                        machine,
                        ledger,
                        AgentPhase.POLICY_VIOLATION,
                        {"reason": "unexpected_action_kind"},
                    )
                    break

                if config.condition is ControllerCondition.DIRECT and action.arguments.get(
                    "validity_assessment"
                ) not in {"valid", "invalid", "uncertain"}:
                    self._transition(
                        writer,
                        sequence,
                        config,
                        task,
                        machine,
                        ledger,
                        AgentPhase.POLICY_VIOLATION,
                        {"reason": "direct_validity_precommit_required"},
                    )
                    break

                if _scientific_revision_due(config.condition, history[:-1]) and not (
                    _candidate_changed(history[:-1], action)
                ):
                    self._transition(
                        writer,
                        sequence,
                        config,
                        task,
                        machine,
                        ledger,
                        AgentPhase.FAILED,
                        {"reason": "scientific_revision_must_change_candidate"},
                    )
                    break

                tool_result, sequence = self._invoke_tool(
                    writer, sequence, config, task, machine, ledger, action
                )
                if tool_result is None:
                    break
                history.append(_observation_record(tool_result.observation))
                if tool_result.observation.ok:
                    if config.condition is ControllerCondition.DIRECT:
                        sequence = self._transition(
                            writer,
                            sequence,
                            config,
                            task,
                            machine,
                            ledger,
                            AgentPhase.FINALIZING,
                            {"reason": "direct_precommitted_candidate"},
                        )
                        grade = evaluator()
                        final_phase = AgentPhase.SUCCEEDED if grade.success else AgentPhase.FAILED
                        self._transition(
                            writer,
                            sequence,
                            config,
                            task,
                            machine,
                            ledger,
                            final_phase,
                            {"grade": grade.to_dict()},
                        )
                        break
                    if _scientific_revision_due(config.condition, history):
                        retries += 1
                        sequence = self._transition(
                            writer,
                            sequence,
                            config,
                            task,
                            machine,
                            ledger,
                            AgentPhase.REVIEWING,
                            {"reason": "successful_candidate_scientific_review"},
                        )
                        try:
                            review_reservation = ledger.reserve(BudgetUsage(retries=1))
                            ledger.reconcile(review_reservation, BudgetUsage(retries=1))
                        except BudgetExceeded:
                            self._transition(
                                writer,
                                sequence,
                                config,
                                task,
                                machine,
                                ledger,
                                AgentPhase.BUDGET_EXCEEDED,
                                {"reason": "scientific_revision_reservation"},
                            )
                            break
                        sequence = self._transition(
                            writer,
                            sequence,
                            config,
                            task,
                            machine,
                            ledger,
                            AgentPhase.EXECUTING,
                        )
                    continue
                if (
                    not tool_result.observation.retryable
                    or not config.condition.retry
                    or retries >= 1
                ):
                    self._transition(
                        writer,
                        sequence,
                        config,
                        task,
                        machine,
                        ledger,
                        AgentPhase.FAILED,
                        {"reason": "tool_failure", "code": tool_result.observation.code},
                    )
                    break

                retries += 1
                sequence = self._transition(
                    writer,
                    sequence,
                    config,
                    task,
                    machine,
                    ledger,
                    AgentPhase.RETRYING,
                )
                try:
                    retry_reservation = ledger.reserve(BudgetUsage(retries=1))
                    ledger.reconcile(retry_reservation, BudgetUsage(retries=1))
                except BudgetExceeded:
                    self._transition(
                        writer,
                        sequence,
                        config,
                        task,
                        machine,
                        ledger,
                        AgentPhase.BUDGET_EXCEEDED,
                        {"reason": "retry_reservation"},
                    )
                    break
                if not config.condition.replan_on_retry:
                    sequence = self._transition(
                        writer,
                        sequence,
                        config,
                        task,
                        machine,
                        ledger,
                        AgentPhase.EXECUTING,
                    )
                    continue
                sequence = self._transition(
                    writer,
                    sequence,
                    config,
                    task,
                    machine,
                    ledger,
                    AgentPhase.REPLANNING,
                )
                replan, sequence, model_calls = self._next_action(
                    writer,
                    sequence,
                    config,
                    task,
                    machine,
                    ledger,
                    history,
                    model_calls,
                )
                if replan is None:
                    break
                if replan.kind is not ActionKind.PLAN:
                    self._transition(
                        writer,
                        sequence,
                        config,
                        task,
                        machine,
                        ledger,
                        AgentPhase.FAILED,
                        {"reason": "replan_required"},
                    )
                    break
                history.append(_action_record(replan))
                sequence = self._transition(
                    writer,
                    sequence,
                    config,
                    task,
                    machine,
                    ledger,
                    AgentPhase.EXECUTING,
                )

            if not machine.terminal:
                self._transition(
                    writer,
                    sequence,
                    config,
                    task,
                    machine,
                    ledger,
                    AgentPhase.FAILED,
                    {"reason": "model_call_limit"},
                )

        return self._result(config, machine, ledger, model_calls, retries, grade)

    def _validate_tools(self, task: TaskSpec) -> None:
        missing = set(task.allowed_tools).difference(self._tools.names)
        if missing:
            raise AgentRunError(f"task allows unregistered tools: {sorted(missing)}")

    def _next_action(
        self,
        writer: TrajectoryWriter,
        sequence: int,
        config: AgentRunConfig,
        task: TaskSpec,
        machine: AgentStateMachine,
        ledger: BudgetLedger,
        history: list[dict[str, Any]],
        model_calls: int,
    ) -> tuple[Action | None, int, int]:
        if model_calls >= config.max_model_calls:
            return None, sequence, model_calls
        try:
            reservation = ledger.reserve(config.model_call_reservation)
        except BudgetExceeded:
            sequence = self._transition(
                writer,
                sequence,
                config,
                task,
                machine,
                ledger,
                AgentPhase.BUDGET_EXCEEDED,
                {"reason": "model_reservation"},
            )
            return None, sequence, model_calls
        started = time.monotonic_ns()
        try:
            result = self._model.complete(
                ModelRequest(
                    instructions=config.instructions,
                    input_text=_policy_input(task, config.condition, machine.phase, history),
                    max_output_tokens=config.max_output_tokens,
                    output_schema=_phase_action_schema(
                        config.action_schema,
                        task,
                        config.condition,
                        machine.phase,
                        history,
                    ),
                )
            )
            actual = BudgetUsage(
                input_tokens=_required_tokens(result.usage.input_tokens),
                output_tokens=_required_tokens(result.usage.output_tokens),
                cost_microusd=config.pricing.cost_microusd(result.usage),
                wall_time_ms=_elapsed_ms(started),
            )
            ledger.reconcile(reservation, actual)
        except BudgetError:
            ledger.cancel(reservation)
            sequence = self._transition(
                writer,
                sequence,
                config,
                task,
                machine,
                ledger,
                AgentPhase.BUDGET_EXCEEDED,
                {"reason": "model_usage_exceeded_reservation"},
            )
            return None, sequence, model_calls + 1
        except (AgentRunError, ModelError, OSError, ValueError):
            ledger.cancel(reservation)
            sequence = self._transition(
                writer,
                sequence,
                config,
                task,
                machine,
                ledger,
                AgentPhase.FAILED,
                {"reason": "model_call_failed"},
            )
            return None, sequence, model_calls + 1
        writer.append(
            TrajectoryEvent(
                sequence=sequence,
                timestamp_utc=_now(),
                run_id=config.run_id,
                task_id=task.task_id,
                event_type="model_action",
                state_before=machine.phase,
                state_after=machine.phase,
                budget=ledger.committed,
                payload={
                    "provider": result.provider,
                    "model": result.model,
                    "response_id": result.response_id,
                    "usage": asdict(result.usage),
                    "action": _action_record(result.action),
                },
            )
        )
        return result.action, sequence + 1, model_calls + 1

    def _invoke_tool(
        self,
        writer: TrajectoryWriter,
        sequence: int,
        config: AgentRunConfig,
        task: TaskSpec,
        machine: AgentStateMachine,
        ledger: BudgetLedger,
        action: Action,
    ) -> tuple[ToolResult | None, int]:
        if action.name not in task.allowed_tools:
            sequence = self._transition(
                writer,
                sequence,
                config,
                task,
                machine,
                ledger,
                AgentPhase.POLICY_VIOLATION,
                {"reason": "tool_not_allowed", "tool": action.name},
            )
            return None, sequence
        try:
            tool = self._tools.resolve(action.name)
            reservation = ledger.reserve(tool.maximum_usage)
        except ToolRegistryError:
            sequence = self._transition(
                writer,
                sequence,
                config,
                task,
                machine,
                ledger,
                AgentPhase.POLICY_VIOLATION,
                {"reason": "tool_not_registered", "tool": action.name},
            )
            return None, sequence
        except BudgetExceeded:
            sequence = self._transition(
                writer,
                sequence,
                config,
                task,
                machine,
                ledger,
                AgentPhase.BUDGET_EXCEEDED,
                {"reason": "tool_reservation", "tool": action.name},
            )
            return None, sequence
        try:
            tool_arguments = dict(action.arguments)
            tool_arguments.pop("validity_assessment", None)
            tool_arguments.pop("revision_reason", None)
            result = tool.handler(tool_arguments)
            ledger.reconcile(reservation, result.usage)
        except BudgetError:
            ledger.cancel(reservation)
            sequence = self._transition(
                writer,
                sequence,
                config,
                task,
                machine,
                ledger,
                AgentPhase.BUDGET_EXCEEDED,
                {"reason": "tool_usage_exceeded_reservation", "tool": action.name},
            )
            return None, sequence
        except (OSError, ToolRegistryError, ValueError):
            ledger.cancel(reservation)
            sequence = self._transition(
                writer,
                sequence,
                config,
                task,
                machine,
                ledger,
                AgentPhase.FAILED,
                {"reason": "tool_execution_failed", "tool": action.name},
            )
            return None, sequence
        writer.append(
            TrajectoryEvent(
                sequence=sequence,
                timestamp_utc=_now(),
                run_id=config.run_id,
                task_id=task.task_id,
                event_type="tool_observation",
                state_before=machine.phase,
                state_after=machine.phase,
                budget=ledger.committed,
                payload={"tool": action.name, "observation": asdict(result.observation)},
            )
        )
        return result, sequence + 1

    @staticmethod
    def _transition(
        writer: TrajectoryWriter,
        sequence: int,
        config: AgentRunConfig,
        task: TaskSpec,
        machine: AgentStateMachine,
        ledger: BudgetLedger,
        target: AgentPhase,
        payload: Mapping[str, Any] | None = None,
    ) -> int:
        before, after = machine.transition(target)
        writer.append(
            TrajectoryEvent(
                sequence=sequence,
                timestamp_utc=_now(),
                run_id=config.run_id,
                task_id=task.task_id,
                event_type="state_transition",
                state_before=before,
                state_after=after,
                budget=ledger.committed,
                payload=payload or {},
            )
        )
        return sequence + 1

    @staticmethod
    def _result(
        config: AgentRunConfig,
        machine: AgentStateMachine,
        ledger: BudgetLedger,
        model_calls: int,
        retries: int,
        grade: GradeReport | None,
    ) -> AgentRunResult:
        return AgentRunResult(
            run_id=config.run_id,
            condition=config.condition,
            phase=machine.phase,
            usage=ledger.committed,
            model_calls=model_calls,
            retries=retries,
            grade=grade,
        )


def _policy_input(
    task: TaskSpec,
    condition: ControllerCondition,
    phase: AgentPhase,
    history: list[dict[str, Any]],
) -> str:
    return json.dumps(
        {
            "task": {
                "task_id": task.task_id,
                "schema_version": task.schema_version,
                "objective": task.objective,
                "allowed_tools": task.allowed_tools,
                "required_artifacts": task.required_artifacts,
                "metadata": dict(task.metadata),
            },
            "condition": condition.value,
            "phase": phase.value,
            "history": history,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _phase_action_schema(
    base_schema: Mapping[str, Any],
    task: TaskSpec,
    condition: ControllerCondition,
    phase: AgentPhase,
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Narrow a compatible action schema to the single kind allowed by runtime state."""
    schema = deepcopy(dict(base_schema))
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return schema
    kind_property = properties.get("kind")
    name_property = properties.get("name")
    if not isinstance(kind_property, dict) or not isinstance(name_property, dict):
        return schema
    if phase in {AgentPhase.PLANNING, AgentPhase.REPLANNING}:
        expected_kind = ActionKind.PLAN.value
        allowed_names = ["draft_plan" if phase is AgentPhase.PLANNING else "revise_plan"]
    elif _last_observation_succeeded(history) and not _scientific_revision_due(condition, history):
        expected_kind = ActionKind.FINAL.value
        allowed_names = ["submit"]
    else:
        expected_kind = ActionKind.TOOL.value
        allowed_names = list(task.allowed_tools)
    kind_property["enum"] = [expected_kind]
    name_property["enum"] = allowed_names
    return schema


def _last_observation_succeeded(history: list[dict[str, Any]]) -> bool:
    if not history:
        return False
    observation = history[-1].get("observation")
    return isinstance(observation, dict) and observation.get("ok") is True


def _scientific_revision_due(condition: ControllerCondition, history: list[dict[str, Any]]) -> bool:
    if not condition.successful_candidate_revision:
        return False
    observations = [
        item["observation"] for item in history if isinstance(item.get("observation"), dict)
    ]
    successful = sum(observation.get("ok") is True for observation in observations)
    failed = any(observation.get("ok") is False for observation in observations)
    return successful == 1 and not failed


def _candidate_changed(history: list[dict[str, Any]], action: Action) -> bool:
    prior_actions = [item for item in history if item.get("kind") == ActionKind.TOOL.value]
    if not prior_actions:
        return True
    ignored = {"validity_assessment", "revision_reason"}
    prior = {
        key: value
        for key, value in prior_actions[-1].get("arguments", {}).items()
        if key not in ignored
    }
    current = {key: value for key, value in action.arguments.items() if key not in ignored}
    if not prior and not current:
        return bool(action.arguments.get("revision_reason"))
    return prior != current


def _action_record(action: Action) -> dict[str, Any]:
    return {"kind": action.kind.value, "name": action.name, "arguments": dict(action.arguments)}


def _observation_record(observation: Observation) -> dict[str, Any]:
    return {
        "observation": {
            "ok": observation.ok,
            "code": observation.code,
            "payload": dict(observation.payload),
            "retryable": observation.retryable,
        }
    }


def _required_tokens(value: int | None) -> int:
    if value is None:
        raise AgentRunError("provider token usage is missing")
    return value


def _elapsed_ms(started_ns: int) -> int:
    return max(0, (time.monotonic_ns() - started_ns) // 1_000_000)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write_manifest(
    path: Path,
    task: TaskSpec,
    config: AgentRunConfig,
    model: ModelAdapter,
) -> None:
    manifest = {
        "run_id": config.run_id,
        "task_id": task.task_id,
        "task_schema_version": task.schema_version,
        "condition": config.condition.value,
        "provider": model.provider,
        "model": model.model,
        "budget": asdict(config.budget),
        "model_call_reservation": asdict(config.model_call_reservation),
        "max_model_calls": config.max_model_calls,
        "max_output_tokens": config.max_output_tokens,
        "pricing": asdict(config.pricing),
    }
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True)
        stream.write("\n")
