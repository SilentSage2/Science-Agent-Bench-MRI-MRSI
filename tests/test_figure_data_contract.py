from __future__ import annotations

import json
import unittest
from pathlib import Path


class FigureDataContractTests(unittest.TestCase):
    def test_baseline_data_is_explicitly_non_agent_and_contract_covers_endpoints(self) -> None:
        data = json.loads(Path("experiments/baseline_figure_data_v1.json").read_text())
        contract = json.loads(Path("protocol/figure_data_contract_v1.json").read_text())

        self.assertFalse(data["research_result"])
        self.assertIn("no agent", data["scope"])
        self.assertEqual(
            {item["family"] for item in data["paired_effects"]},
            {
                "mri_multicoil",
                "mrsi_nuisance",
            },
        )
        agent_fields = contract["figure_contracts"]["figure_3_agent_endpoints"]["required_fields"]
        self.assertIn("technically_completed", agent_fields)
        self.assertIn("scientifically_valid", agent_fields)
        self.assertIn("invalidity_detected", agent_fields)


if __name__ == "__main__":
    unittest.main()
