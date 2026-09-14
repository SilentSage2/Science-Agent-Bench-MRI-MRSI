from __future__ import annotations

import json
from pathlib import Path

from science_agent.agent import ControllerCondition

ROOT = Path(__file__).resolve().parents[1]


def test_adversarial_fixture_covers_every_condition_and_resolves_tests() -> None:
    fixture = json.loads(
        (ROOT / "protocol" / "controller_adversarial_fixtures_v1.json").read_text(encoding="utf-8")
    )
    cases = fixture["cases"]

    assert {case["condition"] for case in cases} == {item.value for item in ControllerCondition}
    assert len({case["case_id"] for case in cases}) == len(cases)
    assert fixture["hidden_scores_visible"] is False
    for case in cases:
        path_text, test_name = case["test"].split("::", 1)
        path = ROOT / path_text
        assert path.is_file()
        assert test_name.split("::")[-1] in path.read_text(encoding="utf-8")
