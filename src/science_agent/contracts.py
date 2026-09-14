"""Strict, serializable contracts shared by policies and the executor."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class ContractError(ValueError):
    """Raised when policy-visible data violates a declared contract."""


class ActionKind(StrEnum):
    PLAN = "plan"
    TOOL = "tool"
    FINAL = "final"


def _reject_unknown(data: Mapping[str, Any], allowed: set[str]) -> None:
    unknown = set(data).difference(allowed)
    if unknown:
        raise ContractError(f"unknown fields: {sorted(unknown)}")


def _non_empty(value: str, field_name: str) -> str:
    if not value.strip():
        raise ContractError(f"{field_name} must not be empty")
    return value


def _string_tuple(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ContractError(f"{field_name} must be a sequence of strings")
    result = tuple(value)
    if not all(isinstance(item, str) and item.strip() for item in result):
        raise ContractError(f"{field_name} must contain non-empty strings")
    return result


def _mapping(value: object, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{field_name} must be a mapping")
    return dict(value)


def _boolean(value: object, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ContractError(f"{field_name} must be a boolean")
    return value


@dataclass(frozen=True, slots=True)
class TaskSpec:
    task_id: str
    schema_version: str
    objective: str
    allowed_tools: tuple[str, ...]
    required_artifacts: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _non_empty(self.task_id, "task_id")
        _non_empty(self.schema_version, "schema_version")
        _non_empty(self.objective, "objective")
        if len(set(self.allowed_tools)) != len(self.allowed_tools):
            raise ContractError("allowed_tools must be unique")
        if len(set(self.required_artifacts)) != len(self.required_artifacts):
            raise ContractError("required_artifacts must be unique")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> TaskSpec:
        allowed = {
            "task_id",
            "schema_version",
            "objective",
            "allowed_tools",
            "required_artifacts",
            "metadata",
        }
        _reject_unknown(data, allowed)
        try:
            return cls(
                task_id=str(data["task_id"]),
                schema_version=str(data["schema_version"]),
                objective=str(data["objective"]),
                allowed_tools=_string_tuple(data["allowed_tools"], "allowed_tools"),
                required_artifacts=_string_tuple(
                    data["required_artifacts"], "required_artifacts"
                ),
                metadata=_mapping(data.get("metadata", {}), "metadata"),
            )
        except (KeyError, TypeError) as exc:
            raise ContractError(f"invalid task specification: {exc}") from exc


@dataclass(frozen=True, slots=True)
class Action:
    kind: ActionKind
    name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _non_empty(self.name, "name")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Action:
        _reject_unknown(data, {"kind", "name", "arguments"})
        try:
            return cls(
                kind=ActionKind(data["kind"]),
                name=str(data["name"]),
                arguments=_mapping(data.get("arguments", {}), "arguments"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ContractError(f"invalid action: {exc}") from exc


@dataclass(frozen=True, slots=True)
class Observation:
    ok: bool
    code: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    retryable: bool = False

    def __post_init__(self) -> None:
        _non_empty(self.code, "code")
        if self.ok and self.retryable:
            raise ContractError("a successful observation cannot be retryable")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Observation:
        _reject_unknown(data, {"ok", "code", "payload", "retryable"})
        try:
            return cls(
                ok=_boolean(data["ok"], "ok"),
                code=str(data["code"]),
                payload=_mapping(data.get("payload", {}), "payload"),
                retryable=_boolean(data.get("retryable", False), "retryable"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ContractError(f"invalid observation: {exc}") from exc
