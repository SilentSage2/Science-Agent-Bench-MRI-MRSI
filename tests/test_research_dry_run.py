from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from science_agent.research_dry_run import run_research_dry_run


class ResearchDryRunTests(unittest.TestCase):
    def test_all_five_conditions_cross_both_research_families(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            summary = run_research_dry_run(Path(temporary) / "dry-run")

        self.assertFalse(summary["research_result"])
        self.assertEqual(summary["provider"], "scripted")
        self.assertEqual(summary["run_count"], 10)
        runs = summary["runs"]
        self.assertEqual({run["family"] for run in runs}, {"mri_multicoil", "mrsi_nuisance"})
        self.assertEqual(
            {run["condition"] for run in runs},
            {"direct", "self_debug", "reactive", "plan_only", "plan_retry_replan"},
        )
        self.assertTrue(all(run["technically_completed"] for run in runs))
        retry_runs = [
            run for run in runs if run["condition"] in {"self_debug", "plan_retry_replan"}
        ]
        self.assertTrue(all(run["retries"] == 1 for run in retry_runs))


if __name__ == "__main__":
    unittest.main()
