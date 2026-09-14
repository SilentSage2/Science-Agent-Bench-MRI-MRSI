"""OpenAI Responses API adapter with an injectable offline transport."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Any, Protocol, cast

from science_agent.contracts import Action, ContractError
from science_agent.model import ModelError, ModelRequest, ModelResult, ModelUsage


class ModelAdapterError(ModelError):
    """Raised when a provider response cannot safely become a benchmark action."""


class JsonTransport(Protocol):
    def post_json(
        self,
        path: str,
        payload: Mapping[str, Any],
        headers: Mapping[str, str],
        timeout_seconds: float,
    ) -> Mapping[str, Any]: ...


class UrllibJsonTransport:
    """Small standard-library HTTPS transport; responses are never persisted here."""

    def __init__(self, base_url: str = "https://api.openai.com/v1") -> None:
        if not base_url.startswith("https://"):
            raise ValueError("base_url must use HTTPS")
        self._base_url = base_url.rstrip("/")

    def post_json(
        self,
        path: str,
        payload: Mapping[str, Any],
        headers: Mapping[str, str],
        timeout_seconds: float,
    ) -> Mapping[str, Any]:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            self._base_url + path,
            data=body,
            headers=dict(headers),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                decoded = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise ModelAdapterError(f"OpenAI request failed with HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ModelAdapterError("OpenAI request failed before a response was received") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ModelAdapterError("OpenAI returned a non-JSON response") from exc
        if not isinstance(decoded, Mapping):
            raise ModelAdapterError("OpenAI returned a non-object response")
        return cast(Mapping[str, Any], decoded)


class OpenAIResponsesAdapter:
    """Convert one Responses API structured output into a validated Action."""

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        timeout_seconds: float = 60.0,
        transport: JsonTransport | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must not be empty")
        if not model.strip():
            raise ValueError("model must not be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._transport = transport or UrllibJsonTransport()

    @classmethod
    def from_env(
        cls,
        model: str,
        *,
        timeout_seconds: float = 60.0,
        transport: JsonTransport | None = None,
    ) -> OpenAIResponsesAdapter:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ModelAdapterError("OPENAI_API_KEY is not set")
        return cls(
            api_key,
            model,
            timeout_seconds=timeout_seconds,
            transport=transport,
        )

    @property
    def provider(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return self._model

    def complete(self, request: ModelRequest) -> ModelResult:
        payload: dict[str, Any] = {
            "model": self._model,
            "instructions": request.instructions,
            "input": request.input_text,
            "max_output_tokens": request.max_output_tokens,
            "store": False,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": request.schema_name,
                    "strict": True,
                    "schema": dict(request.output_schema),
                }
            },
        }
        response = self._transport.post_json(
            "/responses",
            payload,
            {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            self._timeout_seconds,
        )
        status = response.get("status")
        if status != "completed":
            raise ModelAdapterError("OpenAI response did not complete")
        response_id = _required_string(response, "id")
        returned_model = _required_string(response, "model")
        action = _parse_action(_extract_output_text(response))
        usage = _parse_usage(response.get("usage"))
        return ModelResult(
            provider=self.provider,
            model=returned_model,
            response_id=response_id,
            action=action,
            usage=usage,
        )


def _required_string(data: Mapping[str, Any], name: str) -> str:
    value = data.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ModelAdapterError(f"OpenAI response is missing {name}")
    return value


def _extract_output_text(response: Mapping[str, Any]) -> str:
    output = response.get("output")
    if not isinstance(output, list):
        raise ModelAdapterError("OpenAI response output is missing")
    pieces: list[str] = []
    for item in output:
        if not isinstance(item, Mapping) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, Mapping) and part.get("type") == "output_text":
                text = part.get("text")
                if isinstance(text, str):
                    pieces.append(text)
    if not pieces:
        raise ModelAdapterError("OpenAI response contains no output_text")
    return "".join(pieces)


def _parse_action(text: str) -> Action:
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ModelAdapterError("OpenAI structured output is not valid JSON") from exc
    if not isinstance(decoded, Mapping):
        raise ModelAdapterError("OpenAI structured output is not a JSON object")
    try:
        return Action.from_dict(decoded)
    except ContractError as exc:
        raise ModelAdapterError("OpenAI structured output violates the Action contract") from exc


def _parse_usage(value: object) -> ModelUsage:
    if value is None:
        return ModelUsage(input_tokens=None, output_tokens=None)
    if not isinstance(value, Mapping):
        raise ModelAdapterError("OpenAI response usage is not an object")
    try:
        return ModelUsage(
            input_tokens=_optional_non_negative_int(value.get("input_tokens"), "input_tokens"),
            output_tokens=_optional_non_negative_int(value.get("output_tokens"), "output_tokens"),
        )
    except ContractError as exc:
        raise ModelAdapterError("OpenAI response usage violates the usage contract") from exc


def _optional_non_negative_int(value: object, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ModelAdapterError(f"OpenAI usage {name} is invalid")
    return value
