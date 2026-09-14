from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from science_agent.tasks.mrs_spectral_fit import (
    create_mrs_fit_fixture,
    grade_mrs_fit,
    solve_mrs_fit_reference,
)


class MRSSpectralFitTaskTests(unittest.TestCase):
    def test_reference_artifact_passes_all_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mrs_fit_fixture(root / "inputs", seed=17)
            solve_mrs_fit_reference(root / "inputs", root / "outputs")
            report = grade_mrs_fit(root / "inputs", root / "outputs")
            self.assertTrue(report.success, report.diagnostics)

    def test_unsupported_model_conclusion_fails_scientific_validity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mrs_fit_fixture(root / "inputs", seed=18)
            solve_mrs_fit_reference(root / "inputs", root / "outputs")
            result_path = root / "outputs" / "result.json"
            result = json.loads(result_path.read_text())
            result["conclusion_code"] = "naa_only_preferred"
            result_path.write_text(json.dumps(result))
            report = grade_mrs_fit(root / "inputs", root / "outputs")
            self.assertFalse(report.scientifically_valid)
            self.assertFalse(report.success)

    def test_non_finite_result_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mrs_fit_fixture(root / "inputs", seed=19)
            solve_mrs_fit_reference(root / "inputs", root / "outputs")
            result_path = root / "outputs" / "result.json"
            result = json.loads(result_path.read_text())
            result["test_rmse"] = float("nan")
            result_path.write_text(json.dumps(result))
            report = grade_mrs_fit(root / "inputs", root / "outputs")
            self.assertFalse(report.artifact_valid)


if __name__ == "__main__":
    unittest.main()
