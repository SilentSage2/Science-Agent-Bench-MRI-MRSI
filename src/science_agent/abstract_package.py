"""Validate the machine-checkable ISMRM abstract-package length contract."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


class AbstractPackageError(ValueError):
    """Raised when a required field is absent or exceeds its working limit."""


@dataclass(frozen=True, slots=True)
class PackageCounts:
    title_characters: int
    synopsis_words: int
    impact_words: int
    body_words: int
    caption_characters: tuple[int, ...]


def validate_package(package_directory: Path, *, submission_ready: bool = False) -> PackageCounts:
    draft = (package_directory / "DRAFT.md").read_text(encoding="utf-8")
    captions_text = (package_directory / "CAPTIONS.md").read_text(encoding="utf-8")
    title = _one(draft, "TITLE")
    synopsis = _one(draft, "SYNOPSIS")
    impact = _one(draft, "IMPACT")
    body = _one(draft, "BODY")
    captions = _many(captions_text, "CAPTION")
    counts = PackageCounts(
        title_characters=len(_visible_text(title)),
        synopsis_words=_word_count(synopsis),
        impact_words=_word_count(impact),
        body_words=_word_count(body),
        caption_characters=tuple(len(_visible_text(caption)) for caption in captions),
    )
    violations: list[str] = []
    if counts.title_characters > 125:
        violations.append(f"title has {counts.title_characters} characters (limit 125)")
    if counts.synopsis_words > 100:
        violations.append(f"synopsis has {counts.synopsis_words} words (limit 100)")
    if counts.impact_words > 40:
        violations.append(f"impact has {counts.impact_words} words (limit 40)")
    if counts.body_words > 750:
        violations.append(f"body has {counts.body_words} words (limit 750)")
    if len(captions) > 5:
        violations.append(f"package has {len(captions)} captions (limit 5)")
    for index, count in enumerate(counts.caption_characters, start=1):
        if count > 500:
            violations.append(f"caption {index} has {count} characters (limit 500)")
    submission_fields = (title, synopsis, impact, body, *captions)
    if submission_ready and any("PLANNED" in value.upper() for value in submission_fields):
        violations.append("submission fields still contain PLANNED evidence placeholders")
    if violations:
        raise AbstractPackageError("; ".join(violations))
    return counts


def _one(text: str, field: str) -> str:
    values = _many(text, field)
    if len(values) != 1:
        raise AbstractPackageError(f"expected exactly one {field} field")
    return values[0]


def _many(text: str, field: str) -> list[str]:
    pattern = re.compile(
        rf"<!-- ISMRM:{field}:START -->\s*(.*?)\s*<!-- ISMRM:{field}:END -->",
        flags=re.DOTALL,
    )
    return pattern.findall(text)


def _visible_text(text: str) -> str:
    value = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    value = re.sub(r"[`*_#\[\]()]", "", value)
    return " ".join(value.split())


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b", _visible_text(text), flags=re.UNICODE))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_directory", type=Path, nargs="?", default=Path("abstract"))
    parser.add_argument(
        "--submission-ready",
        action="store_true",
        help="also reject unresolved PLANNED evidence placeholders",
    )
    arguments = parser.parse_args()
    counts = validate_package(
        arguments.package_directory,
        submission_ready=arguments.submission_ready,
    )
    print(
        "abstract package passes 2026 working limits: "
        f"title={counts.title_characters} chars, synopsis={counts.synopsis_words} words, "
        f"impact={counts.impact_words} words, body={counts.body_words} words, "
        f"captions={list(counts.caption_characters)} chars"
    )


if __name__ == "__main__":
    main()
