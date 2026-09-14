from __future__ import annotations

import json
import os
import unittest
from collections.abc import Mapping
from typing import Any
from unittest.mock import patch

from science_agent.contracts import ActionKind
from science_agent.model import ModelRequest
from science_agent.openai_responses import ModelAdapterError, OpenAIResponsesAdapter


class RecordingTransport:
    def __init__(self, response: Mapping[str, Any]) -> None:
        self.response = response
        self.path: str | None = None
        self.payload: Mapping[str, Any] | None = None
        self.headers: Mapping[str, str] | None = None
        self.timeout_seconds: float | None = None

    def post_json(
        self,
        path: str,
        payload: Mapping[str, Any],
        headers: Mapping[str, str],
        timeout_seconds: float,
    ) -> Mapping[str, Any]:
        self.path = path
        self.payload = payload
        self.headers = headers
        self.timeout_seconds = timeout_seconds
        return self.response


def _request() -> ModelRequest:
    return ModelRequest(
        instructions="Return the next benchmark action.",
        input_text="Inspect the public task state.",
        max_output_tokens=128,
        output_schema={
            "type": "object",
            "properties": {
                "kind": {"type": "string"},
                "name": {"type": "string"},
                "arguments": {"type": "object"},
            },
            "required": ["kind", "name", "arguments"],
            "additionalProperties": False,
        },
    )


def _response(action: Mapping[str, Any] | None = None) -> dict[str, Any]:
    action = action or {"kind": "plan", "name": "draft_plan", "arguments": {}}
    return {
        "id": "resp_test",
        "model": "gpt-test-2026-01-01",
        "status": "completed",
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": json.dumps(action)}],
            }
        ],
        "usage": {"input_tokens": 41, "output_tokens": 17, "total_tokens": 58},
    }


class OpenAIResponsesAdapterTests(unittest.TestCase):
    def test_builds_non_stored_structured_request_and_parses_action(self) -> None:
        transport = RecordingTransport(_response())
        adapter = OpenAIResponsesAdapter(
            "test-secret",
            "gpt-test",
            timeout_seconds=12.5,
            transport=transport,
        )

        result = adapter.complete(_request())

        self.assertEqual(result.provider, "openai")
        self.assertEqual(result.model, "gpt-test-2026-01-01")
        self.assertEqual(result.action.kind, ActionKind.PLAN)
        self.assertEqual(result.usage.input_tokens, 41)
        self.assertEqual(transport.path, "/responses")
        self.assertEqual(transport.timeout_seconds, 12.5)
        assert transport.payload is not None
        self.assertFalse(transport.payload["store"])
        self.assertEqual(transport.payload["max_output_tokens"], 128)
        text = transport.payload["text"]
        assert isinstance(text, Mapping)
        output_format = text["format"]
        assert isinstance(output_format, Mapping)
        self.assertEqual(output_format["type"], "json_schema")
        self.assertTrue(output_format["strict"])
        assert transport.headers is not None
        self.assertEqual(transport.headers["Authorization"], "Bearer test-secret")

    def test_missing_usage_stays_unknown(self) -> None:
        response = _response()
        del response["usage"]
        adapter = OpenAIResponsesAdapter(
            "test-secret", "gpt-test", transport=RecordingTransport(response)
        )

        result = adapter.complete(_request())

        self.assertFalse(result.usage.complete)

    def test_rejects_non_completed_response(self) -> None:
        response = _response()
        response["status"] = "incomplete"
        adapter = OpenAIResponsesAdapter(
            "test-secret", "gpt-test", transport=RecordingTransport(response)
        )

        with self.assertRaisesRegex(ModelAdapterError, "did not complete"):
            adapter.complete(_request())

    def test_rejects_invalid_usage(self) -> None:
        response = _response()
        response["usage"] = {"input_tokens": -1, "output_tokens": 2}
        adapter = OpenAIResponsesAdapter(
            "test-secret", "gpt-test", transport=RecordingTransport(response)
        )

        with self.assertRaisesRegex(ModelAdapterError, "usage"):
            adapter.complete(_request())

    def test_rejects_invalid_action_without_echoing_content(self) -> None:
        adapter = OpenAIResponsesAdapter(
            "test-secret",
            "gpt-test",
            transport=RecordingTransport(_response({"kind": "shell", "name": "unsafe"})),
        )

        with self.assertRaisesRegex(ModelAdapterError, "violates the Action contract"):
            adapter.complete(_request())

    def test_from_env_fails_closed_without_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ModelAdapterError, "OPENAI_API_KEY is not set"):
                OpenAIResponsesAdapter.from_env("gpt-test")


if __name__ == "__main__":
    unittest.main()
