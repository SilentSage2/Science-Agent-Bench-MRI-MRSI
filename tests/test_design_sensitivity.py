from __future__ import annotations

import json
import unittest
from pathlib import Path

from science_agent.design_sensitivity import required_paired_instances


class DesignSensitivityTests(unittest.TestCase):
    def test_required_instances_matches_frozen_working_example(self) -> None:
        result = required_paired_instances(
            absolute_effect=0.20,
            discordant_probability=0.35,
        )

        self.assertEqual(result.required_instances, 61)

    def test_smaller_effect_requires_more_instances(self) -> None:
        small = required_paired_instances(
            absolute_effect=0.10,
            discordant_probability=0.35,
        )
        large = required_paired_instances(
            absolute_effect=0.20,
            discordant_probability=0.35,
        )

        self.assertGreater(small.required_instances, large.required_instances)

    def test_impossible_effect_discordance_pair_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            required_paired_instances(
                absolute_effect=0.30,
                discordant_probability=0.20,
            )

    def test_blinded_primary_design_matches_calculation_and_independence(self) -> None:
        root = Path(__file__).resolve().parents[1]
        design = json.loads(
            (root / "protocol" / "blinded_primary_design_v1.json").read_text(encoding="utf-8")
        )
        assumptions = design["design_assumptions"]
        calculated = required_paired_instances(
            absolute_effect=assumptions["absolute_paired_effect"],
            discordant_probability=assumptions["discordant_pair_probability"],
            alpha=assumptions["two_sided_alpha"],
            power=assumptions["power"],
        )

        self.assertEqual(calculated.required_instances, 61)
        self.assertEqual(
            assumptions["required_independent_instances_per_family"],
            calculated.required_instances,
        )
        self.assertEqual(sum(design["difficulty_allocation_per_family"].values()), 61)
        self.assertEqual(design["planned_independent_instances_total"], 122)
        self.assertEqual(design["planned_runs_total"], 1220)
        self.assertFalse(design["uses_primary_outcomes"])


if __name__ == "__main__":
    unittest.main()
