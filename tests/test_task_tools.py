from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from science_agent.task_tools import (
    TaskBindingError,
    bind_mri_leakage_reference,
    bind_mri_reconstruction_reference,
    bind_mrs_fit_reference,
    bind_mrsi_nuisance_reference,
)
from science_agent.tasks import (
    create_mri_leakage_fixture,
    create_mri_reconstruction_fixture,
    create_mrs_fit_fixture,
    create_mrsi_nuisance_fixture,
)


class ReferenceTaskBindingTests(unittest.TestCase):
    def test_mrs_fit_binding_creates_artifacts_that_pass_grading(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            outputs = root / "outputs"
            create_mrs_fit_fixture(inputs, seed=1701)
            binding = bind_mrs_fit_reference(inputs, outputs)

            result = binding.tools.resolve(binding.task.allowed_tools[0]).handler({})

            self.assertTrue(result.observation.ok)
            self.assertTrue(binding.evaluator().success)
            self.assertGreater(result.usage.artifact_bytes, 0)

    def test_mri_leakage_binding_creates_artifacts_that_pass_grading(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            outputs = root / "outputs"
            create_mri_leakage_fixture(inputs, seed=2301, include_violations=True)
            binding = bind_mri_leakage_reference(inputs, outputs)

            result = binding.tools.resolve(binding.task.allowed_tools[0]).handler({})

            self.assertTrue(result.observation.ok)
            self.assertTrue(binding.evaluator().success)

    def test_mri_reconstruction_binding_keeps_reference_evaluator_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            evaluator = root / "evaluator"
            outputs = root / "outputs"
            create_mri_reconstruction_fixture(inputs, evaluator, seed=3101, matrix_size=8)
            binding = bind_mri_reconstruction_reference(inputs, evaluator, outputs)

            result = binding.tools.resolve(binding.task.allowed_tools[0]).handler({})

            self.assertTrue(result.observation.ok)
            self.assertTrue(binding.evaluator().success)
            self.assertNotIn("reference", json.dumps(dict(binding.task.metadata)).lower())

    def test_mrsi_nuisance_binding_creates_artifacts_that_pass_grading(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            evaluator = root / "evaluator"
            outputs = root / "outputs"
            create_mrsi_nuisance_fixture(inputs, evaluator, seed=4101, grid_size=2)
            binding = bind_mrsi_nuisance_reference(inputs, evaluator, outputs)

            result = binding.tools.resolve(binding.task.allowed_tools[0]).handler({})

            self.assertTrue(result.observation.ok)
            self.assertTrue(binding.evaluator().success)

    def test_model_cannot_override_fixed_paths_with_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            outputs = root / "outputs"
            create_mrs_fit_fixture(inputs, seed=1701)
            binding = bind_mrs_fit_reference(inputs, outputs)

            result = binding.tools.resolve(binding.task.allowed_tools[0]).handler(
                {"output_directory": "/tmp/escape"}
            )

            self.assertFalse(result.observation.ok)
            self.assertEqual(result.observation.code, "unexpected_tool_arguments")
            self.assertFalse(outputs.exists())

    def test_task_id_mismatch_is_rejected_before_agent_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / "inputs"
            create_mrs_fit_fixture(inputs, seed=1701)
            metadata_path = inputs / "task.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["task_id"] = "WRONG"
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

            with self.assertRaises(TaskBindingError):
                bind_mrs_fit_reference(inputs, root / "outputs")


if __name__ == "__main__":
    unittest.main()
