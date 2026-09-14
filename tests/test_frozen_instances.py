from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from science_agent.frozen_instances import materialize_frozen_instances


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
            for instance in first["instances"]:
                task_path = root / "first" / instance["instance_id"] / "inputs" / "task.json"
                public_task = json.loads(task_path.read_text(encoding="utf-8"))
                self.assertNotIn("seed", public_task)
                self.assertNotIn("reference", json.dumps(public_task).lower())


if __name__ == "__main__":
    unittest.main()
