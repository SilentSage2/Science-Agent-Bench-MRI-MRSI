from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from science_agent.budget import BudgetUsage
from science_agent.state import AgentPhase
from science_agent.trajectory import (
    TrajectoryError,
    TrajectoryEvent,
    TrajectoryWriter,
    sha256_file,
)


def event(sequence: int) -> TrajectoryEvent:
    return TrajectoryEvent(
        sequence=sequence,
        timestamp_utc="2026-09-14T16:00:00Z",
        run_id="run-1",
        task_id="SAB-MRS-FIT-001-dev-1",
        event_type="state_transition",
        state_before=AgentPhase.READY,
        state_after=AgentPhase.EXECUTING,
        budget=BudgetUsage(tool_calls=sequence),
        payload={"source": "test"},
    )


class TrajectoryTests(unittest.TestCase):
    def test_jsonl_is_stable_and_hashable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trajectory.jsonl"
            with TrajectoryWriter(path) as writer:
                writer.append(event(0))
                writer.append(event(1))

            records = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([record["sequence"] for record in records], [0, 1])
            self.assertEqual(records[0]["state_after"], "executing")
            self.assertEqual(len(sha256_file(path)), 64)

    def test_existing_trajectory_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trajectory.jsonl"
            path.write_text("existing\n")
            with self.assertRaises(FileExistsError):
                TrajectoryWriter(path)
            self.assertEqual(path.read_text(), "existing\n")

    def test_sequence_must_be_monotonic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trajectory.jsonl"
            with TrajectoryWriter(path) as writer:
                with self.assertRaises(TrajectoryError):
                    writer.append(event(1))


if __name__ == "__main__":
    unittest.main()
