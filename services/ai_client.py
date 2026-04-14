"""
Reusable HTTP client for the OpenRouter API.

This module is the ONLY place in the codebase that talks to OpenRouter.
All other services use `call_llm()` or `call_openrouter()` and receive
the LLM's text response (or a raised exception on failure).

Features:
  • call_llm(prompt) — simple single-prompt interface
  • call_openrouter(messages) — full multi-message interface
  • Automatic retries with exponential back-off for transient errors
  • Structured logging of every request/response cycle
  • Timeout protection to prevent indefinite hangs
"""

import time
import requests

from config import (
    get_api_key,
    OPENROUTER_API_URL,
    DEFAULT_MODEL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF_FACTOR,
)
from utils.logger import get_logger

logger = get_logger()


class OpenRouterError(Exception):
    """Raised when the OpenRouter API returns an error or an unexpected response."""


# ═══════════════════════════════════════════════════════════════════
# Simple interface — for most use cases
# ═══════════════════════════════════════════════════════════════════

def call_llm(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.3,
    max_tokens: int = 1024,
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Send a single prompt to the LLM and return the response text.

    This is the preferred interface for most services. It wraps
    call_openrouter() with a simpler signature.

    Args:
        prompt:        The user message / input to process.
        system_prompt: Optional system-level instructions.
        temperature:   Sampling temperature (lower = more deterministic).
        max_tokens:    Maximum tokens in the completion.
        model:         OpenRouter model identifier.

    Returns:
        The LLM's text response.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    return call_openrouter(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


# ═══════════════════════════════════════════════════════════════════
# Full interface — for multi-message conversations
# ═══════════════════════════════════════════════════════════════════

def call_openrouter(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    """
    Send a chat-completion request to OpenRouter and return the response text.

    Args:
        messages:    List of {"role": ..., "content": ...} message dicts.
        model:       OpenRouter model identifier.
        temperature: Sampling temperature (lower = more deterministic).
        max_tokens:  Maximum tokens in the completion.

    Returns:
        The text content of the first choice in the API response.

    Raises:
        OpenRouterError: On API errors, timeouts, or malformed responses.
    """
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://customer-support-automation.internal",
        "X-Title": "AI Customer Support Automation",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    last_exception: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug(
                f"OpenRouter request (attempt {attempt}/{MAX_RETRIES}) — "
                f"model={model}, temp={temperature}"
            )

            response = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )

            # ── Handle HTTP errors ───────────────────────────────
            if response.status_code != 200:
                error_body = response.text
                logger.error(
                    f"OpenRouter HTTP {response.status_code}: {error_body}"
                )

                # Rate-limit or server error → retry
                if response.status_code in (429, 500, 502, 503, 504):
                    last_exception = OpenRouterError(
                        f"HTTP {response.status_code}: {error_body}"
                    )
                    _wait_before_retry(attempt)
                    continue

                # Client error (400, 401, 403, etc.) → no point retrying
                raise OpenRouterError(
                    f"HTTP {response.status_code}: {error_body}"
                )

            # ── Parse successful response ────────────────────────
            data = response.json()

            choices = data.get("choices")
            if not choices or not isinstance(choices, list):
                raise OpenRouterError(
                    f"Unexpected response structure — no 'choices' field: {data}"
                )

            content = choices[0].get("message", {}).get("content", "").strip()
            if not content:
                raise OpenRouterError(
                    f"Empty content in response: {data}"
                )

            logger.debug(f"OpenRouter response: {content[:200]}...")
            return content

        except requests.exceptions.Timeout:
            logger.warning(f"Request timed out (attempt {attempt}/{MAX_RETRIES})")
            last_exception = OpenRouterError("Request timed out")
            _wait_before_retry(attempt)

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error (attempt {attempt}/{MAX_RETRIES}): {e}")
            last_exception = OpenRouterError(f"Connection error: {e}")
            _wait_before_retry(attempt)

    # All retries exhausted
    raise OpenRouterError(
        f"All {MAX_RETRIES} attempts failed. Last error: {last_exception}"
    )


def _wait_before_retry(attempt: int) -> None:
    """Sleep with exponential back-off before the next retry."""
    wait = RETRY_BACKOFF_FACTOR ** attempt
    logger.info(f"Retrying in {wait:.1f}s...")
    time.sleep(wait)
