from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from science_agent.tasks.mri_reconstruction import (
    create_mri_reconstruction_fixture,
    grade_mri_reconstruction,
    solve_mri_reconstruction_reference,
)


class MRIReconstructionTaskTests(unittest.TestCase):
    def test_reference_reconstruction_passes_all_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mri_reconstruction_fixture(
                root / "inputs", root / "evaluator", seed=31, matrix_size=8
            )
            solve_mri_reconstruction_reference(root / "inputs", root / "outputs")
            report = grade_mri_reconstruction(root / "inputs", root / "evaluator", root / "outputs")
            self.assertTrue(report.success, report.diagnostics)
            self.assertLessEqual(report.metrics["nrmse"], 0.9)

    def test_hidden_reference_is_not_in_policy_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mri_reconstruction_fixture(
                root / "inputs", root / "evaluator", seed=32, matrix_size=8
            )
            self.assertFalse((root / "inputs" / "reference.csv").exists())
            self.assertTrue((root / "evaluator" / "reference.csv").exists())

    def test_modified_pixel_breaks_data_consistency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mri_reconstruction_fixture(
                root / "inputs", root / "evaluator", seed=33, matrix_size=8
            )
            solve_mri_reconstruction_reference(root / "inputs", root / "outputs")
            reconstruction_path = root / "outputs" / "reconstruction.csv"
            with reconstruction_path.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            rows[0]["value"] = str(float(rows[0]["value"]) + 0.5)
            with reconstruction_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=("y", "x", "value"))
                writer.writeheader()
                writer.writerows(rows)
            report = grade_mri_reconstruction(root / "inputs", root / "evaluator", root / "outputs")
            self.assertFalse(report.numerical_correct)
            self.assertIn("sampled_kspace_not_preserved", report.diagnostics)

    def test_fabricated_consistency_metric_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mri_reconstruction_fixture(
                root / "inputs", root / "evaluator", seed=34, matrix_size=8
            )
            solve_mri_reconstruction_reference(root / "inputs", root / "outputs")
            result_path = root / "outputs" / "result.json"
            result = json.loads(result_path.read_text())
            result["reported_data_consistency_rmse"] = 0.25
            result_path.write_text(json.dumps(result))
            report = grade_mri_reconstruction(root / "inputs", root / "evaluator", root / "outputs")
            self.assertFalse(report.numerical_correct)
            self.assertIn("reported_consistency_does_not_match", report.diagnostics)


if __name__ == "__main__":
    unittest.main()
