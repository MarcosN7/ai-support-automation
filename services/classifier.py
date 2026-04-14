"""
STEP 1 — Message Classification Service.

Takes a raw customer message and returns one of the predefined categories
along with a confidence score.
Loads the classification prompt from an external .txt file and validates
the LLM's output against the allowed category list.
"""

import json
from typing import Tuple

from config import VALID_CATEGORIES, CLASSIFICATION_TEMPERATURE
from prompts.prompt_loader import load_prompt
from services.ai_client import call_llm
from utils.logger import get_logger

logger = get_logger()

# Prompt file loaded once and cached
PROMPT_FILE = "classification_prompt.txt"


def classify_message(message: str) -> Tuple[str, float]:
    """
    Classify a customer message into one of the predefined categories.

    Args:
        message: The raw customer support message.

    Returns:
        A tuple of (category_string, confidence_score).
        Falls back to ("Other", 0.0) if the LLM fails or returns invalid JSON.
    """
    logger.info(f"Classifying message: {message[:80]}...")

    system_prompt = load_prompt(PROMPT_FILE)

    raw_response = call_llm(
        prompt=message,
        system_prompt=system_prompt,
        temperature=CLASSIFICATION_TEMPERATURE,
        max_tokens=150,   # Needs room for JSON
    )

    try:
        # Strip potential markdown blocks (e.g., ```json ... ```)
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        data = json.loads(cleaned_response)
        category = data.get("category", "Other")
        confidence = float(data.get("confidence", 0.0))

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Classification JSON parse failed: {e}. Raw response: {raw_response}")
        return "Other", 0.0

    # Clean up the category — strip whitespace, quotes, trailing periods
    category = category.strip().strip('"').strip("'").rstrip(".")

    # Validate against known categories (case-insensitive fuzzy match)
    for valid in VALID_CATEGORIES:
        if category.lower() == valid.lower():
            logger.info(f"Classification result: {valid} (Confidence: {confidence})")
            return valid, confidence

    # Fallback: if the model returned something unexpected, default to "Other"
    logger.warning(
        f"Unrecognized category '{category}' -- defaulting to 'Other' with low confidence"
    )
    return "Other", 0.0
