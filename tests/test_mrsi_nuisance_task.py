from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from science_agent.tasks.mrsi_nuisance_removal import (
    create_mrsi_nuisance_fixture,
    grade_mrsi_nuisance,
    solve_mrsi_nuisance_reference,
)


class MRSINuisanceTaskTests(unittest.TestCase):
    def test_reference_correction_passes_all_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mrsi_nuisance_fixture(root / "inputs", root / "evaluator", seed=41, grid_size=2)
            solve_mrsi_nuisance_reference(root / "inputs", root / "outputs")
            report = grade_mrsi_nuisance(root / "inputs", root / "evaluator", root / "outputs")
            self.assertTrue(report.success, report.diagnostics)
            self.assertGreater(report.metrics["mean_water_suppression_db"], 20.0)
            self.assertGreater(report.metrics["mean_lipid_suppression_db"], 20.0)
            self.assertLess(report.metrics["mean_metabolite_retention_nrmse"], 0.2)

    def test_clean_reference_is_evaluator_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mrsi_nuisance_fixture(root / "inputs", root / "evaluator", seed=42, grid_size=2)
            self.assertFalse((root / "inputs" / "clean_reference.csv").exists())
            self.assertTrue((root / "evaluator" / "clean_reference.csv").exists())

    def test_corrupted_corrected_spectrum_fails_thresholds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mrsi_nuisance_fixture(root / "inputs", root / "evaluator", seed=43, grid_size=2)
            solve_mrsi_nuisance_reference(root / "inputs", root / "outputs")
            path = root / "outputs" / "corrected_spectra.csv"
            with path.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            rows[0]["corrected_signal"] = "10.0"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=("voxel_id", "frequency_ppm", "corrected_signal"),
                )
                writer.writeheader()
                writer.writerows(rows)
            report = grade_mrsi_nuisance(root / "inputs", root / "evaluator", root / "outputs")
            self.assertFalse(report.numerical_correct)
            self.assertFalse(report.scientifically_valid)

    def test_fabricated_summary_metric_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mrsi_nuisance_fixture(root / "inputs", root / "evaluator", seed=44, grid_size=2)
            solve_mrsi_nuisance_reference(root / "inputs", root / "outputs")
            result_path = root / "outputs" / "result.json"
            result = json.loads(result_path.read_text())
            result["mean_water_suppression_db"] = 999.0
            result_path.write_text(json.dumps(result))
            report = grade_mrsi_nuisance(root / "inputs", root / "evaluator", root / "outputs")
            self.assertFalse(report.numerical_correct)
            self.assertIn("incorrect_mean_water_suppression_db", report.diagnostics)


if __name__ == "__main__":
    unittest.main()
