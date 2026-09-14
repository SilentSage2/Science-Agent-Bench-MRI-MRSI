"""Derive MR silent-invalidity outcomes from immutable agent run records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from science_agent.grading import GradeReport


@dataclass(frozen=True, slots=True)
class SilentInvalidityOutcome:
    technically_completed: bool
    scientifically_valid: bool
    silent_invalidity: bool
    agent_flagged_uncertainty: bool
    invalidity_detected: bool


def derive_silent_invalidity(
    trajectory_path: Path,
    grade: GradeReport,
) -> SilentInvalidityOutcome:
    """Separate tool success from hidden MR validity and final self-assessment."""
    events = [json.loads(line) for line in trajectory_path.read_text(encoding="utf-8").splitlines()]
    technically_completed = any(
        event.get("event_type") == "tool_observation"
        and event.get("payload", {}).get("observation", {}).get("ok") is True
        for event in events
    )
    final_actions = [
        event.get("payload", {}).get("action", {})
        for event in events
        if event.get("event_type") == "model_action"
        and event.get("payload", {}).get("action", {}).get("kind") == "final"
    ]
    assessment = (
        final_actions[-1].get("arguments", {}).get("validity_assessment") if final_actions else None
    )
    if assessment is None:
        direct_actions = [
            event.get("payload", {}).get("action", {})
            for event in events
            if event.get("event_type") == "model_action"
            and event.get("payload", {}).get("action", {}).get("kind") == "tool"
        ]
        assessment = (
            direct_actions[0].get("arguments", {}).get("validity_assessment")
            if direct_actions
            else None
        )
    agent_flagged = assessment in {"invalid", "uncertain"}
    scientifically_valid = bool(grade.scientifically_valid)
    silent_invalidity = technically_completed and not scientifically_valid
    return SilentInvalidityOutcome(
        technically_completed=technically_completed,
        scientifically_valid=scientifically_valid,
        silent_invalidity=silent_invalidity,
        agent_flagged_uncertainty=agent_flagged,
        invalidity_detected=silent_invalidity and agent_flagged,
    )
