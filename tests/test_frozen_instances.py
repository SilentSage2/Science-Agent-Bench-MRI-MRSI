from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from science_agent.frozen_instances import (
    FrozenInstanceError,
    audit_dependence_groups,
    materialize_frozen_instances,
)
from science_agent.primary_manifest import create_primary_manifest


class FrozenInstanceTests(unittest.TestCase):
    def test_manifest_materializes_deterministically_without_public_hidden_fields(self) -> None:
        manifest = Path("protocol/frozen_development_instances_v1.json")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = materialize_frozen_instances(manifest, root / "first")
            second = materialize_frozen_instances(manifest, root / "second")

            self.assertEqual(first, second)
            self.assertEqual(first["instance_count"], 18)
            dependence_groups = {item["dependence_group"] for item in first["instances"]}
            self.assertLess(len(dependence_groups), first["instance_count"])
            self.assertFalse(first["dependence_audit"]["one_instance_per_dependence_group"])
            self.assertFalse(first["dependence_audit"]["primary_candidate"])
            for instance in first["instances"]:
                task_path = root / "first" / instance["instance_id"] / "inputs" / "task.json"
                public_task = json.loads(task_path.read_text(encoding="utf-8"))
                self.assertNotIn("seed", public_task)
                self.assertNotIn("reference", json.dumps(public_task).lower())

    def test_primary_candidate_passes_unique_dependence_audit(self) -> None:
        manifest = create_primary_manifest(
            Path("protocol/blinded_primary_design_v1.json"),
            Path("protocol/primary_manifest_spec_v1.json"),
            b"a" * 32,
        )

        audit = audit_dependence_groups(manifest)

        self.assertTrue(audit["one_instance_per_dependence_group"])
        self.assertTrue(audit["primary_candidate"])
        self.assertEqual(audit["family_counts"]["mri_multicoil"]["dependence_group_count"], 61)
        self.assertEqual(audit["family_counts"]["mrsi_nuisance"]["dependence_group_count"], 61)

    def test_primary_candidate_with_reused_group_fails_closed(self) -> None:
        manifest = create_primary_manifest(
            Path("protocol/blinded_primary_design_v1.json"),
            Path("protocol/primary_manifest_spec_v1.json"),
            b"b" * 32,
        )
        manifest["instances"][1]["dependence_group"] = manifest["instances"][0]["dependence_group"]

        with self.assertRaisesRegex(FrozenInstanceError, "one instance"):
            audit_dependence_groups(manifest)


if __name__ == "__main__":
    unittest.main()
