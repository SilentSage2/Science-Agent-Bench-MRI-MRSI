"""Provider-neutral model request and response contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from science_agent.contracts import Action, ContractError


class ModelError(RuntimeError):
    """Provider-neutral failure at the model boundary."""


@dataclass(frozen=True, slots=True)
class ModelRequest:
    """One bounded request for the policy's next structured action."""

    instructions: str
    input_text: str
    max_output_tokens: int
    output_schema: Mapping[str, Any]
    schema_name: str = "science_agent_action"

    def __post_init__(self) -> None:
        for name in ("instructions", "input_text", "schema_name"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ContractError(f"{name} must be a non-empty string")
        if (
            isinstance(self.max_output_tokens, bool)
            or not isinstance(self.max_output_tokens, int)
            or self.max_output_tokens <= 0
        ):
            raise ContractError("max_output_tokens must be a positive integer")
        if not isinstance(self.output_schema, Mapping) or not self.output_schema:
            raise ContractError("output_schema must be a non-empty mapping")


@dataclass(frozen=True, slots=True)
class ModelUsage:
    """Provider-reported usage; missing values stay unknown instead of becoming zero."""

    input_tokens: int | None
    output_tokens: int | None

    def __post_init__(self) -> None:
        for name in ("input_tokens", "output_tokens"):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value < 0
            ):
                raise ContractError(f"{name} must be a non-negative integer or None")

    @property
    def complete(self) -> bool:
        return self.input_tokens is not None and self.output_tokens is not None


@dataclass(frozen=True, slots=True)
class ModelResult:
    provider: str
    model: str
    response_id: str
    action: Action
    usage: ModelUsage


class ModelAdapter(Protocol):
    """Replaceable boundary between a benchmark policy and a model provider."""

    @property
    def provider(self) -> str: ...

    @property
    def model(self) -> str: ...

    def complete(self, request: ModelRequest) -> ModelResult: ...
