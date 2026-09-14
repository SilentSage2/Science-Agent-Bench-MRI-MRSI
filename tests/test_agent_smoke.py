from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from science_agent.agent_smoke import run_agent_smoke


class AgentSmokeTests(unittest.TestCase):
    def test_all_conditions_and_task_bindings_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "agent-smoke"
            summary = run_agent_smoke(output)

            self.assertEqual(summary["total_runs"], 20)
            self.assertEqual(summary["successes"], 20)
            self.assertFalse(summary["research_result"])
            self.assertEqual(json.loads((output / "metrics.json").read_text()), summary)
            runs = summary["runs"]
            assert isinstance(runs, list)
            self.assertEqual(
                {run["condition"] for run in runs},
                {
                    "direct",
                    "self_debug",
                    "reactive",
                    "plan_only",
                    "plan_retry_replan",
                },
            )
            self.assertEqual(len({run["task_id"] for run in runs}), 4)
            for run in runs:
                run_directory = output / "runs" / run["run_id"]
                self.assertTrue((run_directory / "run_manifest.json").is_file())
                self.assertTrue((run_directory / "trajectory.jsonl").is_file())
                self.assertTrue((run_directory / "artifacts").is_dir())


if __name__ == "__main__":
    unittest.main()
