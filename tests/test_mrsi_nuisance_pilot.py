from __future__ import annotations

import unittest

from science_agent.mrsi_nuisance_pilot import run_pilot


class MRSINuisancePilotTests(unittest.TestCase):
    def test_frozen_pilot_separates_adaptive_from_fixed(self) -> None:
        summary = run_pilot()

        self.assertFalse(summary["research_result"])
        self.assertEqual(summary["case_count"], 9)
        self.assertEqual(summary["adaptive_better_case_count"], 9)
        self.assertGreater(summary["mean_spectral_nrmse_improvement_adaptive_over_fixed"], 0.0)
        self.assertIn("not independent", summary["scientific_unit_warning"])


if __name__ == "__main__":
    unittest.main()
