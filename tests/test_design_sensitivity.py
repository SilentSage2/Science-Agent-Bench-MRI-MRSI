from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
