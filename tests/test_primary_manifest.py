from __future__ import annotations

import unittest
from pathlib import Path

from science_agent.primary_manifest import (
    PrimaryManifestError,
    create_primary_manifest,
    manifest_commitment,
    validate_primary_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "protocol" / "blinded_primary_design_v1.json"
SPEC = ROOT / "protocol" / "primary_manifest_spec_v1.json"


class PrimaryManifestTests(unittest.TestCase):
    def test_manifest_is_sensitivity_sized_independent_and_deterministic(self) -> None:
        first = create_primary_manifest(DESIGN, SPEC, b"a" * 32)
        second = create_primary_manifest(DESIGN, SPEC, b"a" * 32)

        self.assertEqual(first, second)
        self.assertEqual(len(first["instances"]), 122)
        self.assertEqual(len({item["dependence_group"] for item in first["instances"]}), 122)
        self.assertEqual(len({item["seed"] for item in first["instances"]}), 122)
        self.assertFalse(first["primary_run_authorized"])
        self.assertEqual(manifest_commitment(first), manifest_commitment(second))

    def test_private_key_changes_seeds_and_commitment_not_design(self) -> None:
        first = create_primary_manifest(DESIGN, SPEC, b"a" * 32)
        second = create_primary_manifest(DESIGN, SPEC, b"b" * 32)

        self.assertNotEqual(
            [item["seed"] for item in first["instances"]],
            [item["seed"] for item in second["instances"]],
        )
        self.assertNotEqual(manifest_commitment(first), manifest_commitment(second))
        self.assertEqual(
            [(item["family"], item["difficulty"]) for item in first["instances"]],
            [(item["family"], item["difficulty"]) for item in second["instances"]],
        )

    def test_duplicate_dependence_group_is_rejected(self) -> None:
        manifest = create_primary_manifest(DESIGN, SPEC, b"c" * 32)
        manifest["instances"][1]["dependence_group"] = manifest["instances"][0]["dependence_group"]
        with self.assertRaisesRegex(PrimaryManifestError, "one instance"):
            validate_primary_manifest(manifest, expected_per_family=61)

    def test_short_private_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(PrimaryManifestError, "32 bytes"):
            create_primary_manifest(DESIGN, SPEC, b"short")


if __name__ == "__main__":
    unittest.main()
