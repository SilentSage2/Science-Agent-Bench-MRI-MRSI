from __future__ import annotations

import unittest

from science_agent.budget import (
    BudgetError,
    BudgetExceeded,
    BudgetLedger,
    BudgetSpec,
    BudgetUsage,
)


class BudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = BudgetLedger(
            BudgetSpec(input_tokens=100, output_tokens=50, cost_microusd=5000, tool_calls=2)
        )

    def test_reservation_is_reconciled_with_actual_usage(self) -> None:
        reservation = self.ledger.reserve(
            BudgetUsage(input_tokens=60, output_tokens=30, cost_microusd=3000, tool_calls=1)
        )
        self.ledger.reconcile(
            reservation,
            BudgetUsage(input_tokens=55, output_tokens=20, cost_microusd=2500, tool_calls=1),
        )
        self.assertEqual(self.ledger.committed.input_tokens, 55)
        self.assertEqual(self.ledger.reserved, BudgetUsage())

    def test_over_budget_action_fails_before_reservation(self) -> None:
        with self.assertRaisesRegex(BudgetExceeded, "input_tokens"):
            self.ledger.reserve(BudgetUsage(input_tokens=101))
        self.assertEqual(self.ledger.committed, BudgetUsage())

    def test_actual_usage_cannot_exceed_reservation(self) -> None:
        reservation = self.ledger.reserve(BudgetUsage(tool_calls=1))
        with self.assertRaises(BudgetError):
            self.ledger.reconcile(reservation, BudgetUsage(tool_calls=2))

    def test_only_one_reservation_can_be_outstanding(self) -> None:
        self.ledger.reserve(BudgetUsage(tool_calls=1))
        with self.assertRaises(BudgetError):
            self.ledger.reserve(BudgetUsage(tool_calls=1))

    def test_boolean_is_not_valid_integer_usage(self) -> None:
        with self.assertRaises(BudgetError):
            BudgetUsage(tool_calls=True)


if __name__ == "__main__":
    unittest.main()

