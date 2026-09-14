from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from science_agent.tasks.mri_leakage_audit import (
    create_mri_leakage_fixture,
    grade_mri_leakage,
    solve_mri_leakage_reference,
)


class LeakageTaskTests(unittest.TestCase):
    def test_violation_fixture_passes_reference_grade(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mri_leakage_fixture(root / "inputs", seed=23, include_violations=True)
            solve_mri_leakage_reference(root / "inputs", root / "outputs")
            report = grade_mri_leakage(root / "inputs", root / "outputs")
            self.assertTrue(report.success, report.diagnostics)

    def test_clean_fixture_has_no_false_positives(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mri_leakage_fixture(root / "inputs", seed=24, include_violations=False)
            solve_mri_leakage_reference(root / "inputs", root / "outputs")
            result = json.loads((root / "outputs" / "result.json").read_text())
            self.assertEqual(result["audit_verdict"], "pass")
            self.assertEqual(sum(result["violation_count_by_class"].values()), 0)
            self.assertTrue(grade_mri_leakage(root / "inputs", root / "outputs").success)

    def test_wrong_verdict_fails_scientific_validity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_mri_leakage_fixture(root / "inputs", seed=25, include_violations=True)
            solve_mri_leakage_reference(root / "inputs", root / "outputs")
            result_path = root / "outputs" / "result.json"
            result = json.loads(result_path.read_text())
            result["audit_verdict"] = "pass"
            result["conclusion_code"] = "valid_experiment"
            result_path.write_text(json.dumps(result))
            report = grade_mri_leakage(root / "inputs", root / "outputs")
            self.assertFalse(report.scientifically_valid)


if __name__ == "__main__":
    unittest.main()
