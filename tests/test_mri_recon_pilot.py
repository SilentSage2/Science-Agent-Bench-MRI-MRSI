from __future__ import annotations

import unittest

from science_agent.mri_recon_pilot import run_pilot


class MRIReconPilotTests(unittest.TestCase):
    def test_frozen_pilot_separates_conventional_from_naive_baseline(self) -> None:
        summary = run_pilot()

        self.assertEqual(summary["case_count"], 9)
        self.assertEqual(summary["sense_cg_better_case_count"], 9)
        self.assertGreater(
            summary["mean_magnitude_nrmse_improvement_sense_cg_over_zero_fill"],
            0.03,
        )
        lower, upper = summary["improvement_bootstrap_95_interval"]
        self.assertGreater(lower, 0.0)
        self.assertGreater(upper, lower)


if __name__ == "__main__":
    unittest.main()
