from __future__ import annotations

import unittest

from science_agent.contracts import Action, ContractError, Observation, TaskSpec


class ContractTests(unittest.TestCase):
    def test_task_rejects_unknown_fields(self) -> None:
        with self.assertRaises(ContractError):
            TaskSpec.from_dict(
                {
                    "task_id": "SAB-MRS-FIT-001-dev-1",
                    "schema_version": "1",
                    "objective": "Fit the declared models.",
                    "allowed_tools": ["python"],
                    "required_artifacts": ["outputs/result.json"],
                    "hidden_answer": 42,
                }
            )

    def test_task_rejects_duplicate_tools(self) -> None:
        with self.assertRaises(ContractError):
            TaskSpec("id", "1", "objective", ("python", "python"), ("result.json",))

    def test_task_rejects_string_instead_of_tool_sequence(self) -> None:
        with self.assertRaises(ContractError):
            TaskSpec.from_dict(
                {
                    "task_id": "id",
                    "schema_version": "1",
                    "objective": "objective",
                    "allowed_tools": "python",
                    "required_artifacts": ["result.json"],
                }
            )

    def test_action_rejects_unknown_kind(self) -> None:
        with self.assertRaises(ContractError):
            Action.from_dict({"kind": "shell", "name": "run", "arguments": {}})

    def test_successful_observation_cannot_be_retryable(self) -> None:
        with self.assertRaises(ContractError):
            Observation(ok=True, code="ok", retryable=True)

    def test_observation_rejects_truthy_string_boolean(self) -> None:
        with self.assertRaises(ContractError):
            Observation.from_dict({"ok": "false", "code": "failed"})


if __name__ == "__main__":
    unittest.main()
