from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from science_agent.protocol_freeze import FREEZE_GROUPS, create_candidate_freeze


class ProtocolFreezeTests(unittest.TestCase):
    def test_candidate_freeze_hashes_every_declared_file(self) -> None:
        root = Path(__file__).resolve().parents[1]
        payload = create_candidate_freeze(
            root,
            source_revision="abc123",
            requested_model="gpt-test-alias",
            executor_image="sha256:" + "a" * 64,
        )

        self.assertFalse(payload["primary_run_authorized"])
        self.assertFalse(payload["model_identity"]["immutable_snapshot_available"])
        for group, paths in FREEZE_GROUPS.items():
            self.assertEqual(set(payload["file_sha256"][group]), set(paths))
            self.assertTrue(
                all(len(digest) == 64 for digest in payload["file_sha256"][group].values())
            )

    def test_candidate_freeze_changes_when_source_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for paths in FREEZE_GROUPS.values():
                for relative in paths:
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("before", encoding="utf-8")
            before = create_candidate_freeze(
                root,
                source_revision="one",
                requested_model="model",
                executor_image="sha256:" + "b" * 64,
            )
            changed = root / next(iter(FREEZE_GROUPS.values()))[0]
            changed.write_text("after", encoding="utf-8")
            after = create_candidate_freeze(
                root,
                source_revision="two",
                requested_model="model",
                executor_image="sha256:" + "b" * 64,
            )

        self.assertNotEqual(before["file_sha256"], after["file_sha256"])

    def test_mutable_image_tag_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "immutable sha256"):
            create_candidate_freeze(
                Path.cwd(),
                source_revision="abc",
                requested_model="model",
                executor_image="latest",
            )

    def test_committed_candidate_lock_matches_source_files(self) -> None:
        root = Path(__file__).resolve().parents[1]
        committed = json.loads(
            (root / "protocol" / "candidate_freeze_v1.json").read_text(encoding="utf-8")
        )
        regenerated = create_candidate_freeze(
            root,
            source_revision=committed["source_revision"],
            requested_model=committed["requested_model"],
            executor_image=committed["executor_image"],
        )

        self.assertEqual(committed, regenerated)


if __name__ == "__main__":
    unittest.main()
