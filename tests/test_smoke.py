from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from science_agent.smoke import run_smoke


class SmokeTests(unittest.TestCase):
    def test_all_conditions_run_same_tasks_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "smoke"
            summary = run_smoke(output)
            self.assertEqual(summary["total_runs"], 6)
            self.assertEqual(summary["successes"], 6)
            self.assertFalse(summary["research_result"])
            persisted = json.loads((output / "metrics.json").read_text())
            self.assertEqual(persisted, summary)
            self.assertEqual(
                {run["condition"] for run in summary["runs"]},
                {"reactive", "plan_only", "plan_retry_replan"},
            )


if __name__ == "__main__":
    unittest.main()
