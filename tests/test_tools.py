from __future__ import annotations

import unittest

from science_agent.budget import BudgetUsage
from science_agent.contracts import Observation
from science_agent.tools import RegisteredTool, ToolRegistry, ToolRegistryError, ToolResult


def _handler(_: object) -> ToolResult:
    return ToolResult(Observation(True, "ok"), BudgetUsage(tool_calls=1))


class ToolRegistryTests(unittest.TestCase):
    def test_duplicate_names_are_rejected(self) -> None:
        tool = RegisteredTool("mri", BudgetUsage(tool_calls=1), _handler)

        with self.assertRaises(ToolRegistryError):
            ToolRegistry((tool, tool))

    def test_registration_requires_one_reserved_call(self) -> None:
        with self.assertRaises(ToolRegistryError):
            RegisteredTool("mri", BudgetUsage(), _handler)

    def test_result_requires_one_accounted_call(self) -> None:
        with self.assertRaises(ToolRegistryError):
            ToolResult(Observation(True, "ok"), BudgetUsage())

    def test_unknown_tool_is_rejected_without_fallback(self) -> None:
        registry = ToolRegistry(())

        with self.assertRaises(ToolRegistryError):
            registry.resolve("shell")


if __name__ == "__main__":
    unittest.main()
