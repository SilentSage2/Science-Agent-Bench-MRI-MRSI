"""Deterministic reservation-based budget accounting."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Final


_DIMENSIONS: Final = (
    "input_tokens",
    "output_tokens",
    "cost_microusd",
    "tool_calls",
    "retries",
    "wall_time_ms",
    "artifact_bytes",
)


class BudgetError(ValueError):
    """Base class for invalid budget operations."""


class BudgetExceeded(BudgetError):
    """Raised before an action whose reservation would exceed a hard limit."""


@dataclass(frozen=True, slots=True)
class BudgetUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cost_microusd: int = 0
    tool_calls: int = 0
    retries: int = 0
    wall_time_ms: int = 0
    artifact_bytes: int = 0

    def __post_init__(self) -> None:
        for field_info in fields(self):
            value = getattr(self, field_info.name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise BudgetError(f"{field_info.name} must be a non-negative integer")

    def plus(self, other: BudgetUsage) -> BudgetUsage:
        values = {name: getattr(self, name) + getattr(other, name) for name in _DIMENSIONS}
        return BudgetUsage(**values)

    def minus(self, other: BudgetUsage) -> BudgetUsage:
        values = {name: getattr(self, name) - getattr(other, name) for name in _DIMENSIONS}
        if any(value < 0 for value in values.values()):
            raise BudgetError("budget subtraction would become negative")
        return BudgetUsage(**values)


@dataclass(frozen=True, slots=True)
class BudgetSpec(BudgetUsage):
    """Hard ceilings. Integer microdollars avoid floating-point cost drift."""


@dataclass(frozen=True, slots=True)
class Reservation:
    reservation_id: int
    maximum: BudgetUsage


class BudgetLedger:
    """Owns committed usage and at most one outstanding action reservation."""

    def __init__(self, limit: BudgetSpec) -> None:
        self._limit = limit
        self._committed = BudgetUsage()
        self._reservation: Reservation | None = None
        self._next_id = 1

    @property
    def committed(self) -> BudgetUsage:
        return self._committed

    @property
    def reserved(self) -> BudgetUsage:
        return self._reservation.maximum if self._reservation else BudgetUsage()

    def reserve(self, maximum: BudgetUsage) -> Reservation:
        if self._reservation is not None:
            raise BudgetError("an action reservation is already outstanding")
        projected = self._committed.plus(maximum)
        exceeded = [
            name for name in _DIMENSIONS if getattr(projected, name) > getattr(self._limit, name)
        ]
        if exceeded:
            raise BudgetExceeded(f"reservation exceeds: {', '.join(exceeded)}")
        reservation = Reservation(self._next_id, maximum)
        self._next_id += 1
        self._reservation = reservation
        return reservation

    def reconcile(self, reservation: Reservation, actual: BudgetUsage) -> None:
        self._require_current(reservation)
        over_reservation = [
            name
            for name in _DIMENSIONS
            if getattr(actual, name) > getattr(reservation.maximum, name)
        ]
        if over_reservation:
            raise BudgetError(f"actual usage exceeds reservation: {', '.join(over_reservation)}")
        self._committed = self._committed.plus(actual)
        self._reservation = None

    def cancel(self, reservation: Reservation) -> None:
        self._require_current(reservation)
        self._reservation = None

    def _require_current(self, reservation: Reservation) -> None:
        if self._reservation != reservation:
            raise BudgetError("reservation is not current")
