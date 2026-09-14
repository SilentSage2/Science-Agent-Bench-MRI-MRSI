from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from science_agent.abstract_package import AbstractPackageError, validate_package


class AbstractPackageTests(unittest.TestCase):
    def test_repository_draft_passes_working_limits(self) -> None:
        counts = validate_package(Path("abstract"))

        self.assertLessEqual(counts.title_characters, 125)
        self.assertLessEqual(counts.synopsis_words, 100)
        self.assertLessEqual(counts.impact_words, 40)
        self.assertLessEqual(counts.body_words, 750)
        self.assertEqual(len(counts.caption_characters), 5)
        self.assertTrue(all(count <= 500 for count in counts.caption_characters))

    def test_repository_draft_is_not_submission_ready(self) -> None:
        with self.assertRaisesRegex(AbstractPackageError, "PLANNED"):
            validate_package(Path("abstract"), submission_ready=True)

    def test_overlong_title_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary)
            package.joinpath("DRAFT.md").write_text(
                "<!-- ISMRM:TITLE:START -->" + "x" * 126 + "<!-- ISMRM:TITLE:END -->\n"
                "<!-- ISMRM:SYNOPSIS:START -->short<!-- ISMRM:SYNOPSIS:END -->\n"
                "<!-- ISMRM:IMPACT:START -->short<!-- ISMRM:IMPACT:END -->\n"
                "<!-- ISMRM:BODY:START -->short<!-- ISMRM:BODY:END -->",
                encoding="utf-8",
            )
            package.joinpath("CAPTIONS.md").write_text("", encoding="utf-8")

            with self.assertRaisesRegex(AbstractPackageError, "title has 126"):
                validate_package(package)


if __name__ == "__main__":
    unittest.main()
