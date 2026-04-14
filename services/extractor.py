"""
STEP 2 — Structured Data Extraction Service.

Extracts order_id and sentiment from a customer message.
Priority is NO LONGER extracted here — it's determined by the
rule-based priority engine in Step 3.

The LLM is expected to return a JSON object, which is then parsed
and validated before being returned.
"""

import json
import re

from config import EXTRACTION_TEMPERATURE, VALID_SENTIMENTS
from prompts.prompt_loader import load_prompt
from services.ai_client import call_llm
from utils.logger import get_logger

logger = get_logger()

# Prompt file loaded once and cached
PROMPT_FILE = "extraction_prompt.txt"


def extract_data(message: str) -> dict:
    """
    Extract structured data from a customer support message.

    Args:
        message: The raw customer support message.

    Returns:
        Dict with keys: order_id (str|None), sentiment (str).
        Note: priority is NOT included — use priority_engine.determine_priority().
    """
    logger.info(f"Extracting data from: {message[:80]}...")

    system_prompt = load_prompt(PROMPT_FILE)

    raw_response = call_llm(
        prompt=message,
        system_prompt=system_prompt,
        temperature=EXTRACTION_TEMPERATURE,
        max_tokens=200,
    )

    # ── Parse JSON from LLM output ──────────────────────────────
    extracted = _parse_json_response(raw_response)

    # ── Validate and sanitize individual fields ──────────────────
    result = {
        "order_id": _sanitize_order_id(extracted.get("order_id")),
        "sentiment": _sanitize_enum(
            extracted.get("sentiment", "Neutral"),
            VALID_SENTIMENTS,
            "Neutral",
        ),
    }

    logger.info(f"Extraction result: {result}")
    return result


def _parse_json_response(raw: str) -> dict:
    """
    Attempt to parse JSON from the LLM response.

    Handles common issues:
      - Markdown code fences (```json ... ```)
      - Leading/trailing whitespace
      - Partial JSON with extra text
    """
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`")

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fallback: try to find a JSON object in the string
    match = re.search(r"\{[^{}]+\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.error(f"Failed to parse JSON from LLM response: {raw}")
    # Return safe defaults so the pipeline continues
    return {"order_id": None, "sentiment": "Neutral"}


def _sanitize_order_id(value) -> str | None:
    """Return the order ID as a string, or None if not present."""
    if value is None or (isinstance(value, str) and value.lower() in ("null", "none", "")):
        return None
    return str(value).strip()


def _sanitize_enum(value: str, valid_values: list[str], default: str) -> str:
    """Case-insensitive enum check with fallback to default."""
    if not isinstance(value, str):
        return default
    for valid in valid_values:
        if value.strip().lower() == valid.lower():
            return valid
    logger.warning(f"Unexpected value '{value}', defaulting to '{default}'")
    return default
