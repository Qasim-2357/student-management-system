"""Thin, isolated client for an external AI provider.

This module is the *only* place in the codebase that is allowed to talk to
an external AI API. It intentionally knows nothing about students, marks,
attendance, or authorization - it accepts a prompt string and returns the
raw text response from the provider. Everything domain-specific lives in
``app.services.ai_analysis``.

Provider: OpenRouter (https://openrouter.ai). OpenRouter exposes an
OpenAI-compatible ``/chat/completions`` endpoint in front of many models,
including a free tier, so this integration requires no paid SDK and no new
third-party dependency (plain ``urllib`` is enough). The default model is
``openrouter/free``, OpenRouter's own auto-router, which picks a
currently-available free model on each request - this avoids hardcoding a
specific free model id, since the free lineup on OpenRouter rotates
frequently.

Credentials are read from environment variables at call time (never
hardcoded, never imported eagerly at module load), so the application can
start normally even when the AI feature is not configured - it only fails
when someone actually tries to use it.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class AIProviderError(Exception):
    """Raised whenever the AI provider cannot be reached or fails."""


class AIProviderNotConfiguredError(AIProviderError):
    """Raised when required AI provider credentials are missing."""


DEFAULT_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/free"
DEFAULT_TIMEOUT_SECONDS = 20
DEFAULT_MAX_TOKENS = 1024


def _get_api_key() -> str:
    api_key = os.getenv("AI_PROVIDER_API_KEY", "").strip()
    if not api_key:
        raise AIProviderNotConfiguredError(
            "AI_PROVIDER_API_KEY is not set; the AI analysis feature is unavailable"
        )
    return api_key


def _get_base_url() -> str:
    return os.getenv("AI_PROVIDER_BASE_URL", "").strip() or DEFAULT_BASE_URL


def _get_model() -> str:
    return os.getenv("AI_PROVIDER_MODEL", "").strip() or DEFAULT_MODEL


def _get_timeout_seconds() -> float:
    raw = os.getenv("AI_PROVIDER_TIMEOUT_SECONDS", "").strip()
    try:
        return float(raw) if raw else DEFAULT_TIMEOUT_SECONDS
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS


def call_ai_provider(prompt: str) -> str:
    """Send ``prompt`` to the configured AI provider (OpenRouter) and
    return the raw text of its response.

    Raises ``AIProviderError`` (or a subclass) on any failure - missing
    configuration, network issues, non-2xx responses, or a response that
    doesn't contain usable text. Callers are expected to catch this and
    fail gracefully rather than let it propagate as a raw exception.
    """
    api_key = _get_api_key()
    base_url = _get_base_url()
    model = _get_model()
    timeout_seconds = _get_timeout_seconds()

    payload = json.dumps(
        {
            "model": model,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        base_url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise AIProviderError(
            f"AI provider returned an error response: {exc.code}"
        ) from exc
    except urllib.error.URLError as exc:
        raise AIProviderError(f"Could not reach AI provider: {exc.reason}") from exc
    except TimeoutError as exc:
        raise AIProviderError("AI provider request timed out") from exc

    try:
        body = json.loads(raw_body)
        text = body["choices"][0]["message"]["content"]
        text = text.strip() if isinstance(text, str) else ""
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise AIProviderError("AI provider returned an unexpected response shape") from exc

    if not text:
        raise AIProviderError("AI provider returned an empty response")

    return text
