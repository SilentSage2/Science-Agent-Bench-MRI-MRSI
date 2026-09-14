"""Append-only JSONL trajectories and artifact hashing."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, TextIO

from science_agent.budget import BudgetUsage
from science_agent.state import AgentPhase


class TrajectoryError(ValueError):
    """Raised when a trajectory would become mutable or non-monotonic."""


@dataclass(frozen=True, slots=True)
class TrajectoryEvent:
    sequence: int
    timestamp_utc: str
    run_id: str
    task_id: str
    event_type: str
    state_before: AgentPhase
    state_after: AgentPhase
    budget: BudgetUsage
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise TrajectoryError("sequence must be non-negative")
        for name in ("timestamp_utc", "run_id", "task_id", "event_type"):
            if not getattr(self, name).strip():
                raise TrajectoryError(f"{name} must not be empty")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["state_before"] = self.state_before.value
        value["state_after"] = self.state_after.value
        return value


class TrajectoryWriter:
    """Creates a new trajectory and refuses to overwrite an existing path."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._stream: TextIO = path.open("x", encoding="utf-8", newline="\n")
        self._next_sequence = 0
        self._closed = False

    def append(self, event: TrajectoryEvent) -> None:
        if self._closed:
            raise TrajectoryError("trajectory is closed")
        if event.sequence != self._next_sequence:
            raise TrajectoryError(
                f"expected sequence {self._next_sequence}, received {event.sequence}"
            )
        serialized = json.dumps(event.to_dict(), sort_keys=True, separators=(",", ":"))
        self._stream.write(serialized + "\n")
        self._stream.flush()
        self._next_sequence += 1

    def close(self) -> None:
        if not self._closed:
            self._stream.close()
            self._closed = True

    def __enter__(self) -> TrajectoryWriter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def sha256_file(path: Path, chunk_size: int = 64 * 1024) -> str:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()

