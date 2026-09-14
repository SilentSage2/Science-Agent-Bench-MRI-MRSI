from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from science_agent.development_figures import (
    PALETTE,
    _calibration_svg,
    _framework_svg,
    render_development_figures,
)

ROOT = Path(__file__).resolve().parents[1]


def test_framework_is_explicitly_no_go_and_paths_are_distinct() -> None:
    svg = _framework_svg()
    assert "PRIMARY STUDY NO-GO" in svg
    assert all(label in svg for label in ("Direct", "Reactive", "Self-debug", "Plan + recovery"))


def test_calibration_figure_rejects_agent_effect_framing() -> None:
    data = json.loads((ROOT / "experiments" / "baseline_figure_data_v1.json").read_text())
    svg = _calibration_svg(data)
    assert "TASK MECHANISM ONLY · NO AGENT EFFECT" in svg
    assert "v4 condition counts excluded" in svg
    assert "MRI magnitude NRMSE" in svg and "MRSI spectral NRMSE" in svg


def test_palette_uses_colorblind_safe_labeled_series() -> None:
    assert PALETTE["blue"] == "#0072B2"
    assert PALETTE["orange"] == "#E69F00"
    assert PALETTE["blue"] != PALETTE["orange"]


def test_renderer_rejects_placeholder_revision_before_writing() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        with pytest.raises(ValueError, match="exact, non-placeholder"):
            render_development_figures(
                ROOT / "experiments" / "baseline_figure_data_v1.json",
                Path(temporary) / "figures",
                Path("unused-font.ttf"),
                source_revision="TO_BE_REPLACED_BY_COMMIT",
            )
