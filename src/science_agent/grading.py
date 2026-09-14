"""Shared deterministic grading contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class GradeReport:
    artifact_valid: bool
    numerical_correct: bool
    scientifically_valid: bool
    reproducible: bool
    diagnostics: tuple[str, ...] = ()

    @property
    def success(self) -> bool:
        return (
            self.artifact_valid
            and self.numerical_correct
            and self.scientifically_valid
            and self.reproducible
        )

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["success"] = self.success
        return value
