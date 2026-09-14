from __future__ import annotations

import unittest

from science_agent.state import AgentPhase, AgentStateMachine, InvalidTransition


class StateMachineTests(unittest.TestCase):
    def test_planned_success_path(self) -> None:
        machine = AgentStateMachine()
        for phase in (
            AgentPhase.PLANNING,
            AgentPhase.EXECUTING,
            AgentPhase.FINALIZING,
            AgentPhase.SUCCEEDED,
        ):
            machine.transition(phase)
        self.assertTrue(machine.terminal)

    def test_reactive_success_path(self) -> None:
        machine = AgentStateMachine()
        machine.transition(AgentPhase.EXECUTING)
        machine.transition(AgentPhase.FINALIZING)
        machine.transition(AgentPhase.SUCCEEDED)
        self.assertTrue(machine.terminal)

    def test_invalid_transition_fails_closed_without_mutation(self) -> None:
        machine = AgentStateMachine()
        with self.assertRaises(InvalidTransition):
            machine.transition(AgentPhase.SUCCEEDED)
        self.assertEqual(machine.phase, AgentPhase.READY)

    def test_terminal_state_cannot_transition(self) -> None:
        machine = AgentStateMachine()
        machine.transition(AgentPhase.EXECUTING)
        machine.transition(AgentPhase.FAILED)
        with self.assertRaises(InvalidTransition):
            machine.transition(AgentPhase.EXECUTING)


if __name__ == "__main__":
    unittest.main()

