from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from science_agent.agent import ControllerCondition
from science_agent.contracts import Action, ActionKind
from science_agent.live_pilot import (
    _action_schema,
    _canonicalize_action,
    _config,
    _select_balanced_instances,
    run_live_pilot,
)
from science_agent.openai_responses import ModelAdapterError


class LivePilotConfigurationTests(unittest.TestCase):
    def test_schema_requires_nullable_fields_for_strict_structured_output(self) -> None:
        schema = _action_schema("mri_multicoil", "reconstruct_multicoil_mri")
        arguments = schema["properties"]["arguments"]

        self.assertFalse(arguments["additionalProperties"])
        self.assertEqual(set(arguments["required"]), set(arguments["properties"]))
        self.assertIn("sense_cg", arguments["properties"]["method"]["enum"])

    def test_every_condition_uses_same_hard_budget_and_pricing(self) -> None:
        configs = [
            _config("test", condition, "mrsi_nuisance", "remove_complex_mrsi_nuisance")
            for condition in ControllerCondition
        ]

        self.assertEqual(len({config.budget for config in configs}), 1)
        self.assertEqual(len({config.pricing for config in configs}), 1)
        self.assertEqual(configs[0].budget.cost_microusd, 60_000)

    def test_missing_credential_fails_before_creating_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "must-not-exist"
            with patch.dict("os.environ", {}, clear=True):
                with self.assertRaisesRegex(ModelAdapterError, "OPENAI_API_KEY"):
                    run_live_pilot(
                        manifest_path=Path("protocol/frozen_development_instances_v1.json"),
                        output_root=output,
                        image="sha256:" + "a" * 64,
                        model="gpt-test",
                        instance_limit=1,
                        total_cost_ceiling_usd=1.0,
                    )
            self.assertFalse(output.exists())

    def test_checkout_selection_balances_task_families(self) -> None:
        instances = [
            {"instance_id": "mri-1", "family": "mri_multicoil"},
            {"instance_id": "mri-2", "family": "mri_multicoil"},
            {"instance_id": "mrsi-1", "family": "mrsi_nuisance"},
        ]

        selected = _select_balanced_instances(instances, 2)

        self.assertEqual(
            {item["family"] for item in selected},
            {
                "mri_multicoil",
                "mrsi_nuisance",
            },
        )

    def test_live_action_canonicalizer_preserves_direct_precommit(self) -> None:
        action = Action(
            ActionKind.TOOL,
            "reconstruct_multicoil_mri",
            {
                "method": "sense_cg",
                "regularization": 0.003,
                "iterations": 40,
                "validity_assessment": "uncertain",
            },
        )

        canonical = _canonicalize_action(action)

        self.assertEqual(
            canonical.arguments,
            {
                "method": "sense_cg",
                "regularization": 0.003,
                "iterations": 40,
                "validity_assessment": "uncertain",
            },
        )


if __name__ == "__main__":
    unittest.main()
