import json
import os
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from app.services.ai_provider import (
    AIProviderError,
    AIProviderNotConfiguredError,
    call_ai_provider,
)


def _make_urlopen_response(payload: dict):
    """Build a context-manager mock that mimics urllib.request.urlopen's
    return value for a successful OpenRouter chat-completions response."""
    response = MagicMock()
    response.read.return_value = json.dumps(payload).encode("utf-8")
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response


class AIProviderOpenRouterTests(unittest.TestCase):
    def setUp(self):
        self.env_patch = patch.dict(
            os.environ,
            {"AI_PROVIDER_API_KEY": "test-openrouter-key"},
            clear=False,
        )
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    # -- request format --------------------------------------------------

    def test_sends_openrouter_request_with_defaults(self):
        success_response = _make_urlopen_response(
            {"choices": [{"message": {"content": "hello"}}]}
        )

        with patch(
            "app.services.ai_provider.urllib.request.urlopen",
            return_value=success_response,
        ) as mock_urlopen:
            result = call_ai_provider("analyze this student")

        self.assertEqual(result, "hello")

        self.assertEqual(mock_urlopen.call_count, 1)
        request = mock_urlopen.call_args[0][0]

        self.assertEqual(request.full_url, "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-openrouter-key")
        self.assertEqual(request.get_header("Content-type"), "application/json")

        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["model"], "openrouter/free")
        self.assertEqual(
            body["messages"], [{"role": "user", "content": "analyze this student"}]
        )

    def test_uses_configured_base_url_and_model(self):
        success_response = _make_urlopen_response(
            {"choices": [{"message": {"content": "hello"}}]}
        )

        with patch.dict(
            os.environ,
            {
                "AI_PROVIDER_BASE_URL": "https://openrouter.ai/api/v1/chat/completions",
                "AI_PROVIDER_MODEL": "meta-llama/llama-3.3-70b-instruct:free",
            },
            clear=False,
        ), patch(
            "app.services.ai_provider.urllib.request.urlopen",
            return_value=success_response,
        ) as mock_urlopen:
            call_ai_provider("prompt")

        request = mock_urlopen.call_args[0][0]
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["model"], "meta-llama/llama-3.3-70b-instruct:free")

    # -- configuration -----------------------------------------------------

    def test_missing_api_key_raises_not_configured_error(self):
        with patch.dict(os.environ, {"AI_PROVIDER_API_KEY": ""}, clear=False):
            with self.assertRaises(AIProviderNotConfiguredError):
                call_ai_provider("prompt")

    # -- failure handling ----------------------------------------------------

    def test_http_error_raises_ai_provider_error(self):
        http_error = urllib.error.HTTPError(
            url="https://openrouter.ai/api/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=None,
        )
        with patch(
            "app.services.ai_provider.urllib.request.urlopen", side_effect=http_error
        ):
            with self.assertRaises(AIProviderError):
                call_ai_provider("prompt")

    def test_url_error_raises_ai_provider_error(self):
        url_error = urllib.error.URLError("connection refused")
        with patch(
            "app.services.ai_provider.urllib.request.urlopen", side_effect=url_error
        ):
            with self.assertRaises(AIProviderError):
                call_ai_provider("prompt")

    def test_malformed_response_shape_raises_ai_provider_error(self):
        bad_response = _make_urlopen_response({"unexpected": "shape"})
        with patch(
            "app.services.ai_provider.urllib.request.urlopen",
            return_value=bad_response,
        ):
            with self.assertRaises(AIProviderError):
                call_ai_provider("prompt")

    def test_empty_content_raises_ai_provider_error(self):
        empty_response = _make_urlopen_response(
            {"choices": [{"message": {"content": "   "}}]}
        )
        with patch(
            "app.services.ai_provider.urllib.request.urlopen",
            return_value=empty_response,
        ):
            with self.assertRaises(AIProviderError):
                call_ai_provider("prompt")


if __name__ == "__main__":
    unittest.main()
