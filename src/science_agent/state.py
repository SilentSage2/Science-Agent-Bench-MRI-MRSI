"""Fail-closed agent state transitions."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class AgentPhase(StrEnum):
    READY = "ready"
    PLANNING = "planning"
    EXECUTING = "executing"
    RETRYING = "retrying"
    REPLANNING = "replanning"
    FINALIZING = "finalizing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BUDGET_EXCEEDED = "budget_exceeded"
    POLICY_VIOLATION = "policy_violation"


TERMINAL_PHASES: Final = frozenset(
    {
        AgentPhase.SUCCEEDED,
        AgentPhase.FAILED,
        AgentPhase.BUDGET_EXCEEDED,
        AgentPhase.POLICY_VIOLATION,
    }
)

_ALLOWED: Final[dict[AgentPhase, frozenset[AgentPhase]]] = {
    AgentPhase.READY: frozenset({AgentPhase.PLANNING, AgentPhase.EXECUTING}),
    AgentPhase.PLANNING: frozenset(
        {AgentPhase.EXECUTING, AgentPhase.FAILED, AgentPhase.BUDGET_EXCEEDED}
    ),
    AgentPhase.EXECUTING: frozenset(
        {
            AgentPhase.EXECUTING,
            AgentPhase.RETRYING,
            AgentPhase.REPLANNING,
            AgentPhase.FINALIZING,
            AgentPhase.FAILED,
            AgentPhase.BUDGET_EXCEEDED,
            AgentPhase.POLICY_VIOLATION,
        }
    ),
    AgentPhase.RETRYING: frozenset(
        {
            AgentPhase.EXECUTING,
            AgentPhase.REPLANNING,
            AgentPhase.FAILED,
            AgentPhase.BUDGET_EXCEEDED,
        }
    ),
    AgentPhase.REPLANNING: frozenset(
        {AgentPhase.EXECUTING, AgentPhase.FAILED, AgentPhase.BUDGET_EXCEEDED}
    ),
    AgentPhase.FINALIZING: frozenset(
        {
            AgentPhase.SUCCEEDED,
            AgentPhase.FAILED,
            AgentPhase.BUDGET_EXCEEDED,
            AgentPhase.POLICY_VIOLATION,
        }
    ),
}


class InvalidTransition(ValueError):
    """Raised when the executor attempts an undeclared state transition."""


class AgentStateMachine:
    def __init__(self) -> None:
        self._phase = AgentPhase.READY

    @property
    def phase(self) -> AgentPhase:
        return self._phase

    @property
    def terminal(self) -> bool:
        return self._phase in TERMINAL_PHASES

    def transition(self, target: AgentPhase) -> tuple[AgentPhase, AgentPhase]:
        allowed = _ALLOWED.get(self._phase, frozenset())
        if target not in allowed:
            message = f"transition {self._phase.value} -> {target.value} is not allowed"
            raise InvalidTransition(message)
        previous = self._phase
        self._phase = target
        return previous, target
