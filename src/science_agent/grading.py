"""Shared deterministic grading contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class GradeReport:
    artifact_valid: bool
    numerical_correct: bool
    scientifically_valid: bool
    reproducible: bool
    diagnostics: tuple[str, ...] = ()
    metrics: Mapping[str, float] = field(default_factory=dict)

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
