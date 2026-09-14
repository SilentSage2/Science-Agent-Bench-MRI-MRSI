from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from science_agent.research.mrsi_nuisance import (
    create_complex_mrsi_instance,
    evaluate_complex_mrsi_baselines,
    grade_complex_mrsi_nuisance,
    run_complex_mrsi_nuisance_removal,
)


class ComplexMRSIResearchTests(unittest.TestCase):
    def test_complex_public_data_and_hidden_components_are_separated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_complex_mrsi_instance(root / "inputs", root / "evaluator", seed=201, grid_size=3)

            self.assertFalse((root / "inputs" / "reference.npz").exists())
            with np.load(root / "inputs" / "spectra.npz", allow_pickle=False) as data:
                self.assertTrue(np.iscomplexobj(data["observed"]))
                self.assertEqual(data["observed"].shape, (9, 256))
            serialized = json.dumps(
                json.loads((root / "inputs" / "task.json").read_text(encoding="utf-8"))
            ).lower()
            task = json.loads((root / "inputs" / "task.json").read_text(encoding="utf-8"))
            self.assertEqual(task["adaptive_shift_steps_range"], [5, 41])
            self.assertTrue(task["adaptive_shift_steps_must_be_odd"])
            self.assertNotIn("seed", serialized)
            self.assertNotIn("reference", serialized)

    def test_adaptive_baseline_separates_from_fixed_under_hard_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_complex_mrsi_instance(
                root / "inputs",
                root / "evaluator",
                seed=202,
                grid_size=3,
                difficulty="hard",
            )

            fixed, adaptive, oracle = evaluate_complex_mrsi_baselines(
                root / "inputs", root / "evaluator"
            )

            self.assertEqual(fixed.method, "fixed_projection")
            self.assertLess(
                adaptive.metrics.nuisance_residual_ratio,
                fixed.metrics.nuisance_residual_ratio,
            )
            self.assertLess(adaptive.metrics.spectral_nrmse, fixed.metrics.spectral_nrmse)
            self.assertLess(oracle.metrics.spectral_nrmse, adaptive.metrics.spectral_nrmse)

    def test_conventional_artifact_passes_hidden_grader(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_complex_mrsi_instance(
                root / "inputs",
                root / "evaluator",
                seed=203,
                grid_size=3,
                difficulty="moderate",
            )
            run_complex_mrsi_nuisance_removal(
                root / "inputs", root / "outputs", method="adaptive_projection", shift_steps=21
            )

            report = grade_complex_mrsi_nuisance(
                root / "inputs", root / "evaluator", root / "outputs"
            )

            self.assertTrue(report.success, report.diagnostics)

    def test_fabricated_public_residual_fails_numerical_check(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            create_complex_mrsi_instance(root / "inputs", root / "evaluator", seed=204, grid_size=3)
            run_complex_mrsi_nuisance_removal(
                root / "inputs", root / "outputs", method="adaptive_projection", shift_steps=21
            )
            path = root / "outputs" / "result.json"
            result = json.loads(path.read_text(encoding="utf-8"))
            result["reported_public_nuisance_residual"] = 0.0
            path.write_text(json.dumps(result), encoding="utf-8")

            report = grade_complex_mrsi_nuisance(
                root / "inputs", root / "evaluator", root / "outputs"
            )

            self.assertFalse(report.numerical_correct)
            self.assertIn("reported_public_residual_does_not_match", report.diagnostics)


if __name__ == "__main__":
    unittest.main()
