from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from science_agent.research.mri_multicoil import (
    create_multicoil_reconstruction_instance,
    evaluate_multicoil_baselines,
    grade_multicoil_reconstruction,
    run_multicoil_reconstruction,
)


class MulticoilMRIResearchTests(unittest.TestCase):
    def test_hidden_reference_and_multicoil_acquisition_are_separated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_multicoil_reconstruction_instance(
                root / "inputs", root / "evaluator", seed=101, matrix_size=32, coils=4
            )

            self.assertFalse((root / "inputs" / "reference.npz").exists())
            with np.load(root / "inputs" / "acquisition.npz", allow_pickle=False) as data:
                self.assertEqual(data["kspace"].shape, (4, 32, 32))
                self.assertEqual(data["sensitivities"].shape, (4, 32, 32))
                self.assertEqual(data["mask"].shape, (32, 32))

    def test_conventional_baseline_improves_over_zero_fill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_multicoil_reconstruction_instance(
                root / "inputs",
                root / "evaluator",
                seed=102,
                matrix_size=32,
                coils=4,
                acceleration=4.0,
                relative_noise=0.02,
            )

            zero_fill, conventional, oracle = evaluate_multicoil_baselines(
                root / "inputs", root / "evaluator"
            )

            self.assertEqual(zero_fill.method, "zero_filled")
            self.assertLess(conventional.metrics.magnitude_nrmse, zero_fill.metrics.magnitude_nrmse)
            self.assertLess(conventional.metrics.gradient_nrmse, zero_fill.metrics.gradient_nrmse)
            self.assertLess(oracle.metrics.magnitude_nrmse, 1e-10)

    def test_conventional_artifact_passes_hidden_grader(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_multicoil_reconstruction_instance(
                root / "inputs", root / "evaluator", seed=103, matrix_size=32, coils=4
            )
            run_multicoil_reconstruction(
                root / "inputs",
                root / "outputs",
                method="sense_cg",
                regularization=0.003,
                iterations=40,
            )

            report = grade_multicoil_reconstruction(
                root / "inputs", root / "evaluator", root / "outputs"
            )

            self.assertTrue(report.success, report.diagnostics)

    def test_fabricated_residual_fails_numerical_check(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_multicoil_reconstruction_instance(
                root / "inputs", root / "evaluator", seed=104, matrix_size=32, coils=4
            )
            run_multicoil_reconstruction(
                root / "inputs",
                root / "outputs",
                method="sense_cg",
                regularization=0.003,
                iterations=40,
            )
            result_path = root / "outputs" / "result.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["reported_sampled_kspace_residual"] = 0.0
            result_path.write_text(json.dumps(result), encoding="utf-8")

            report = grade_multicoil_reconstruction(
                root / "inputs", root / "evaluator", root / "outputs"
            )

            self.assertFalse(report.numerical_correct)
            self.assertIn("reported_residual_does_not_match", report.diagnostics)


if __name__ == "__main__":
    unittest.main()
