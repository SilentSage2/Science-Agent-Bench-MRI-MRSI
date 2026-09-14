# ruff: noqa: E501
"""Render explicitly non-result framework and task-calibration figures."""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import pairwise
from pathlib import Path
from typing import Any

WIDTH = 1800
HEIGHT = 1100
PALETTE = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "magenta": "#CC79A7",
    "ink": "#17212B",
    "muted": "#5D6B78",
    "paper": "#FFFFFF",
    "panel": "#F4F7F9",
}


def render_development_figures(
    data_path: Path,
    output: Path,
    font_path: Path,
    *,
    source_revision: str,
) -> None:
    if not source_revision.strip() or source_revision == "TO_BE_REPLACED_BY_COMMIT":
        raise ValueError("an exact, non-placeholder source revision is required")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if data.get("research_result") is not False:
        raise ValueError("development Figure 2 requires explicitly non-result calibration data")
    output.mkdir(parents=True, exist_ok=False)
    (output / "figure_1_framework.svg").write_text(_framework_svg(), encoding="utf-8")
    (output / "figure_2_task_calibration.svg").write_text(_calibration_svg(data), encoding="utf-8")
    _render_framework_png(output / "figure_1_framework.png", font_path)
    _render_calibration_png(data, output / "figure_2_task_calibration.png", font_path)
    _phone_preview(output / "figure_1_framework.png", output / "figure_1_framework_phone.png")
    _phone_preview(
        output / "figure_2_task_calibration.png", output / "figure_2_task_calibration_phone.png"
    )
    for figure_id, filename, status in (
        ("figure_1_framework", "figure_1_framework", "IMPLEMENTED-DESIGN"),
        ("figure_2_task_calibration", "figure_2_task_calibration", "TASK-CALIBRATION"),
    ):
        sidecar = {
            "figure_id": figure_id,
            "data_status": status,
            "research_result": False,
            "agent_effect_claim_allowed": False,
            "source_revision": source_revision,
            "source_data_sha256": _sha256(data_path),
            "renderer_sha256": _sha256(Path(__file__)),
            "font": str(font_path),
            "font_sha256": _sha256(font_path),
            "palette": PALETTE,
            "exports": {
                "svg": f"{filename}.svg",
                "png": f"{filename}.png",
                "phone_preview": f"{filename}_phone.png",
            },
            "qa": {
                "canvas_pixels": [WIDTH, HEIGHT],
                "phone_preview_width_pixels": 480,
                "color_encoding_redundant_with_labels": True,
                "colorblind_palette": "Okabe-Ito subset",
                "caption_present": True,
                "provenance_present": True,
                "visual_inspection": "PENDING",
                "mr_domain_signoff": "PENDING",
            },
        }
        (output / f"{filename}.json").write_text(
            json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


def _framework_svg() -> str:
    boxes = [
        (
            80,
            270,
            360,
            "MRI / MRSI tasks",
            "Versioned public inputs\nPrivate evaluator reference",
            "blue",
        ),
        (
            490,
            270,
            410,
            "Controller intervention",
            "Direct · Reactive · Self-debug\nPlan and recovery paths",
            "magenta",
        ),
        (
            950,
            270,
            340,
            "Bounded execution",
            "Allowlisted MR tools\nDigest-pinned Docker",
            "orange",
        ),
        (
            1340,
            270,
            380,
            "Independent grading",
            "Public observations\nHidden physics + fidelity",
            "green",
        ),
    ]
    elements = [
        _svg_header("Failure-aware MR agent evaluation", "IMPLEMENTED DESIGN · PRIMARY STUDY NO-GO")
    ]
    for index, (x, y, width, title, body, color) in enumerate(boxes):
        elements.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="230" rx="24" fill="{PALETTE["panel"]}" stroke="{PALETTE[color]}" stroke-width="6"/>'
        )
        elements.append(_svg_text(x + 24, y + 60, title, 30, PALETTE["ink"], "700"))
        for line_index, line in enumerate(body.split("\n")):
            elements.append(
                _svg_text(x + 24, y + 122 + 42 * line_index, line, 24, PALETTE["muted"])
            )
        if index < len(boxes) - 1:
            elements.append(_svg_arrow(x + width + 10, y + 110, boxes[index + 1][0] - 12, y + 110))
    paths = [
        ("Direct", "choose + assess → execute", "blue"),
        ("Reactive", "choose → observe → assess", "green"),
        ("Self-debug", "choose → observe → revise → assess", "magenta"),
        ("Plan + recovery", "plan → execute → typed failure → replan", "orange"),
    ]
    for index, (label, flow, color) in enumerate(paths):
        y = 620 + index * 76
        elements.append(f'<circle cx="115" cy="{y}" r="13" fill="{PALETTE[color]}"/>')
        elements.append(_svg_text(150, y + 9, label, 29, PALETTE["ink"], "700"))
        elements.append(_svg_text(410, y + 9, flow, 28, PALETTE["muted"]))
    elements.append(
        _svg_footer(
            "Technical completion ≠ scientific validity · hidden references never enter the policy"
        )
    )
    return _svg_document(elements)


def _calibration_svg(data: dict[str, Any]) -> str:
    elements = [_svg_header("MR task calibration", "TASK MECHANISM ONLY · NO AGENT EFFECT")]
    families = (
        ("mri_multicoil", "MRI magnitude NRMSE", 0.36),
        ("mrsi_nuisance", "MRSI spectral NRMSE", 1.9),
    )
    for panel_index, (family, label, maximum) in enumerate(families):
        x0 = 100 + panel_index * 860
        elements.append(
            f'<rect x="{x0}" y="240" width="780" height="650" rx="20" fill="{PALETTE["panel"]}"/>'
        )
        elements.append(_svg_text(x0 + 40, 300, label, 34, PALETTE["ink"], "700"))
        rows = [item for item in data["series"] if item["family"] == family]
        for index, row in enumerate(rows):
            y = 390 + index * 155
            elements.append(
                _svg_text(
                    x0 + 40, y + 30, str(row["difficulty"]).title(), 27, PALETTE["ink"], "700"
                )
            )
            for bar_index, (key, color, name) in enumerate(
                (
                    ("naive_primary_metric", "orange", "Naive"),
                    ("conventional_primary_metric", "blue", "Conventional"),
                )
            ):
                value = float(row[key])
                bar_y = y + 48 + bar_index * 45
                width = 500 * value / maximum
                elements.append(
                    f'<rect x="{x0 + 180}" y="{bar_y}" width="{width:.1f}" height="28" rx="7" fill="{PALETTE[color]}"/>'
                )
                elements.append(
                    _svg_text(
                        x0 + 190 + width, bar_y + 24, f"{name} {value:.3f}", 22, PALETTE["ink"]
                    )
                )
    elements.append(
        _svg_footer(
            "Lower is better · 9 generated cases/family · v4 condition counts excluded · not prevalence"
        )
    )
    return _svg_document(elements)


def _svg_header(title: str, badge: str) -> str:
    return "".join(
        (
            _svg_text(80, 95, title, 54, PALETTE["ink"], "700"),
            f'<rect x="80" y="135" width="720" height="54" rx="27" fill="{PALETTE["ink"]}"/>',
            _svg_text(110, 172, badge, 25, PALETTE["paper"], "700"),
        )
    )


def _svg_footer(text: str) -> str:
    return _svg_text(80, 1050, text, 25, PALETTE["muted"], "700")


def _svg_text(x: float, y: float, value: str, size: int, color: str, weight: str = "400") -> str:
    escaped = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escaped}</text>'


def _svg_arrow(x1: float, y1: float, x2: float, y2: float) -> str:
    return f'<path d="M{x1},{y1} L{x2},{y2} M{x2 - 16},{y2 - 12} L{x2},{y2} L{x2 - 16},{y2 + 12}" fill="none" stroke="{PALETTE["ink"]}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'


def _svg_document(elements: list[str]) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"><rect width="100%" height="100%" fill="{PALETTE["paper"]}"/>{"".join(elements)}</svg>\n'


def _render_framework_png(path: Path, font_path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore[import-not-found]

    image = Image.new("RGB", (WIDTH, HEIGHT), PALETTE["paper"])
    draw = ImageDraw.Draw(image)
    fonts = _fonts(ImageFont, font_path)
    _png_header(
        draw, fonts, "Failure-aware MR agent evaluation", "IMPLEMENTED DESIGN · PRIMARY STUDY NO-GO"
    )
    boxes = [
        (
            80,
            270,
            360,
            "MRI / MRSI tasks",
            "Versioned public inputs\nPrivate evaluator reference",
            "blue",
        ),
        (
            490,
            270,
            410,
            "Controller intervention",
            "Direct · Reactive · Self-debug\nPlan and recovery paths",
            "magenta",
        ),
        (
            950,
            270,
            340,
            "Bounded execution",
            "Allowlisted MR tools\nDigest-pinned Docker",
            "orange",
        ),
        (
            1340,
            270,
            380,
            "Independent grading",
            "Public observations\nHidden physics + fidelity",
            "green",
        ),
    ]
    for x, y, width, title, body, color in boxes:
        draw.rounded_rectangle(
            (x, y, x + width, y + 230), 24, fill=PALETTE["panel"], outline=PALETTE[color], width=6
        )
        draw.text((x + 24, y + 30), title, font=fonts["box"], fill=PALETTE["ink"])
        draw.multiline_text(
            (x + 24, y + 105), body, font=fonts["body"], fill=PALETTE["muted"], spacing=14
        )
    for left, right in pairwise(boxes):
        _png_arrow(draw, left[0] + left[2] + 10, 385, right[0] - 12, 385)
    paths = [
        ("Direct", "choose + assess → execute", "blue"),
        ("Reactive", "choose → observe → assess", "green"),
        ("Self-debug", "choose → observe → revise → assess", "magenta"),
        ("Plan + recovery", "plan → execute → typed failure → replan", "orange"),
    ]
    for index, (label, flow, color) in enumerate(paths):
        y = 620 + index * 78
        draw.ellipse((90, y - 10, 114, y + 14), fill=PALETTE[color])
        draw.text((145, y - 20), label, font=fonts["label"], fill=PALETTE["ink"])
        draw.text((470, y - 20), flow, font=fonts["body"], fill=PALETTE["muted"])
    draw.text(
        (80, 1020),
        "Technical completion ≠ scientific validity · hidden references never enter the policy",
        font=fonts["small"],
        fill=PALETTE["muted"],
    )
    image.save(path, dpi=(300, 300))


def _render_calibration_png(data: dict[str, Any], path: Path, font_path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (WIDTH, HEIGHT), PALETTE["paper"])
    draw = ImageDraw.Draw(image)
    fonts = _fonts(ImageFont, font_path)
    _png_header(draw, fonts, "MR task calibration", "TASK MECHANISM ONLY · NO AGENT EFFECT")
    families = (
        ("mri_multicoil", "MRI magnitude NRMSE", 0.36),
        ("mrsi_nuisance", "MRSI spectral NRMSE", 1.9),
    )
    for panel_index, (family, label, maximum) in enumerate(families):
        x0 = 80 + panel_index * 870
        draw.rounded_rectangle((x0, 240, x0 + 820, 890), 20, fill=PALETTE["panel"])
        draw.text((x0 + 35, 275), label, font=fonts["box"], fill=PALETTE["ink"])
        rows = [item for item in data["series"] if item["family"] == family]
        for index, row in enumerate(rows):
            y = 380 + index * 155
            draw.text(
                (x0 + 35, y),
                str(row["difficulty"]).title(),
                font=fonts["label"],
                fill=PALETTE["ink"],
            )
            for bar_index, (key, color, name) in enumerate(
                (
                    ("naive_primary_metric", "orange", "Naive"),
                    ("conventional_primary_metric", "blue", "Conventional"),
                )
            ):
                value = float(row[key])
                bar_y = y + 48 + bar_index * 48
                width = int(480 * value / maximum)
                draw.rounded_rectangle(
                    (x0 + 190, bar_y, x0 + 190 + width, bar_y + 30), 7, fill=PALETTE[color]
                )
                draw.text(
                    (x0 + 205 + width, bar_y - 2),
                    f"{name} {value:.3f}",
                    font=fonts["tiny"],
                    fill=PALETTE["ink"],
                )
    draw.text(
        (80, 1020),
        "Lower is better · 9 generated cases/family · v4 condition counts excluded · not prevalence",
        font=fonts["small"],
        fill=PALETTE["muted"],
    )
    image.save(path, dpi=(300, 300))


def _fonts(image_font: Any, font_path: Path) -> dict[str, Any]:
    return {
        "title": image_font.truetype(str(font_path), 56),
        "badge": image_font.truetype(str(font_path), 26),
        "box": image_font.truetype(str(font_path), 34),
        "label": image_font.truetype(str(font_path), 30),
        "body": image_font.truetype(str(font_path), 27),
        "small": image_font.truetype(str(font_path), 24),
        "tiny": image_font.truetype(str(font_path), 21),
    }


def _png_header(draw: Any, fonts: dict[str, Any], title: str, badge: str) -> None:
    draw.text((80, 48), title, font=fonts["title"], fill=PALETTE["ink"])
    draw.rounded_rectangle((80, 135, 800, 190), 27, fill=PALETTE["ink"])
    draw.text((110, 148), badge, font=fonts["badge"], fill=PALETTE["paper"])


def _png_arrow(draw: Any, x1: int, y1: int, x2: int, y2: int) -> None:
    draw.line((x1, y1, x2, y2), fill=PALETTE["ink"], width=6)
    draw.line((x2 - 16, y2 - 12, x2, y2), fill=PALETTE["ink"], width=6)
    draw.line((x2 - 16, y2 + 12, x2, y2), fill=PALETTE["ink"], width=6)


def _phone_preview(source: Path, destination: Path) -> None:
    from PIL import Image

    with Image.open(source) as image:
        height = round(image.height * 480 / image.width)
        image.resize((480, height)).save(destination)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--source-revision", required=True)
    arguments = parser.parse_args()
    render_development_figures(
        arguments.data,
        arguments.output,
        arguments.font,
        source_revision=arguments.source_revision,
    )


if __name__ == "__main__":
    main()
