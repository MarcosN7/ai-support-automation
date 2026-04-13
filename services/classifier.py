"""
STEP 1 — Message Classification Service.

Takes a raw customer message and returns one of the predefined categories.
Uses the classification prompt template and validates the LLM's output
against the allowed category list.
"""

from config import VALID_CATEGORIES, CLASSIFICATION_TEMPERATURE
from prompts.classification import build_classification_messages
from services.openrouter_client import call_openrouter
from utils.logger import get_logger

logger = get_logger()


def classify_message(message: str) -> str:
    """
    Classify a customer message into one of the predefined categories.

    Args:
        message: The raw customer support message.

    Returns:
        A category string from VALID_CATEGORIES.
        Falls back to "Other" if the LLM returns an unrecognized value.
    """
    logger.info(f"Classifying message: {message[:80]}...")

    messages = build_classification_messages(message)
    raw_category = call_openrouter(
        messages=messages,
        temperature=CLASSIFICATION_TEMPERATURE,
        max_tokens=50,  # Category names are short
    )

    # Clean up the LLM output — strip whitespace, quotes, trailing periods
    category = raw_category.strip().strip('"').strip("'").rstrip(".")

    # Validate against known categories (case-insensitive fuzzy match)
    for valid in VALID_CATEGORIES:
        if category.lower() == valid.lower():
            logger.info(f"Classification result: {valid}")
            return valid

    # Fallback: if the model returned something unexpected, default to "Other"
    logger.warning(
        f"Unrecognized category '{category}' — defaulting to 'Other'"
    )
    return "Other"
