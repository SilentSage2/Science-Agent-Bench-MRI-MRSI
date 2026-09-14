"""Deterministic model adapter used only for offline orchestration tests."""

from __future__ import annotations

from science_agent.contracts import Action
from science_agent.model import ModelError, ModelRequest, ModelResult, ModelUsage

_DEFAULT_USAGE = ModelUsage(input_tokens=10, output_tokens=5)


class ScriptedModelAdapter:
    def __init__(
        self,
        actions: tuple[Action, ...],
        *,
        usage_per_call: ModelUsage = _DEFAULT_USAGE,
    ) -> None:
        if not actions:
            raise ValueError("actions must not be empty")
        self._actions = actions
        self._usage = usage_per_call
        self._index = 0

    @property
    def provider(self) -> str:
        return "scripted"

    @property
    def model(self) -> str:
        return "scripted-reference-v1"

    def complete(self, request: ModelRequest) -> ModelResult:
        del request
        if self._index >= len(self._actions):
            raise ModelError("scripted actions are exhausted")
        action = self._actions[self._index]
        self._index += 1
        return ModelResult(
            provider=self.provider,
            model=self.model,
            response_id=f"scripted-{self._index}",
            action=action,
            usage=self._usage,
        )
