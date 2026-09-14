from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_review_packet_manifest_references_existing_files() -> None:
    manifest = json.loads(
        (ROOT / "review" / "REVIEW_PACKET_MANIFEST.json").read_text(encoding="utf-8")
    )

    assert manifest["packet_status"] == "no-go-unreviewed"
    assert manifest["primary_run_authorized"] is False
    assert len(manifest["required_roles"]) == 3
    assert set(manifest["known_blocking_issues"]) == {
        "CTRL-001",
        "CTRL-002",
        "STAT-001",
        "MRSI-001",
    }
    for relative_path in manifest["forms"] + manifest["source_material"]:
        assert (ROOT / relative_path).is_file(), relative_path


def test_unsigned_packet_cannot_look_approved() -> None:
    signoff = (ROOT / "review" / "SIGNOFF.md").read_text(encoding="utf-8")
    issue_log = (ROOT / "review" / "ISSUE_LOG.md").read_text(encoding="utf-8")

    assert "NO-GO" in signoff
    assert "UNREVIEWED" in signoff
    assert "| Open |" in issue_log
