from __future__ import annotations

import unittest

from science_agent.contracts import ContractError
from science_agent.model import ModelRequest, ModelUsage


class ModelContractTests(unittest.TestCase):
    def test_request_requires_positive_token_limit(self) -> None:
        with self.assertRaises(ContractError):
            ModelRequest("instructions", "input", 0, {"type": "object"})

    def test_request_rejects_non_integer_token_limit(self) -> None:
        with self.assertRaises(ContractError):
            ModelRequest("instructions", "input", "128", {"type": "object"})  # type: ignore[arg-type]

    def test_missing_usage_remains_unknown(self) -> None:
        usage = ModelUsage(input_tokens=None, output_tokens=None)

        self.assertFalse(usage.complete)

    def test_usage_rejects_boolean_token_count(self) -> None:
        with self.assertRaises(ContractError):
            ModelUsage(input_tokens=True, output_tokens=1)


if __name__ == "__main__":
    unittest.main()
