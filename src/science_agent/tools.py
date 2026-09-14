"""Explicit tool registry for policy-visible MRI/MRSI operations."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from science_agent.budget import BudgetUsage
from science_agent.contracts import Observation


class ToolRegistryError(ValueError):
    """Raised when a tool registration or invocation is invalid."""


@dataclass(frozen=True, slots=True)
class ToolResult:
    observation: Observation
    usage: BudgetUsage

    def __post_init__(self) -> None:
        if self.usage.tool_calls != 1:
            raise ToolRegistryError("a tool result must account for exactly one tool call")


ToolHandler = Callable[[Mapping[str, Any]], ToolResult]


@dataclass(frozen=True, slots=True)
class RegisteredTool:
    name: str
    maximum_usage: BudgetUsage
    handler: ToolHandler

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ToolRegistryError("tool name must not be empty")
        if self.maximum_usage.tool_calls != 1:
            raise ToolRegistryError("a registered tool must reserve exactly one tool call")


class ToolRegistry:
    """Immutable name-to-tool mapping; no dynamic imports or shell fallback."""

    def __init__(self, tools: tuple[RegisteredTool, ...]) -> None:
        by_name = {tool.name: tool for tool in tools}
        if len(by_name) != len(tools):
            raise ToolRegistryError("registered tool names must be unique")
        self._tools = MappingProxyType(by_name)

    @property
    def names(self) -> frozenset[str]:
        return frozenset(self._tools)

    def resolve(self, name: str) -> RegisteredTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolRegistryError(f"tool is not registered: {name}") from exc
