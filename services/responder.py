"""
STEP 3 — Response Generation Service.

Generates a professional, empathetic customer support reply using
context from the classification and extraction steps.
"""

from config import RESPONSE_TEMPERATURE
from prompts.response import build_response_messages
from services.openrouter_client import call_openrouter
from utils.logger import get_logger

logger = get_logger()


def generate_response(
    message: str,
    category: str,
    extracted_data: dict,
) -> str:
    """
    Generate a customer-facing support reply.

    Args:
        message:        The original customer message.
        category:       Classification result from Step 1.
        extracted_data: Dict with order_id, priority, sentiment from Step 2.

    Returns:
        A polished, human-sounding support reply (plain text).
    """
    logger.info(f"Generating response for category='{category}'...")

    messages = build_response_messages(
        customer_message=message,
        category=category,
        order_id=extracted_data.get("order_id"),
        priority=extracted_data.get("priority", "Medium"),
        sentiment=extracted_data.get("sentiment", "Neutral"),
    )

    response = call_openrouter(
        messages=messages,
        temperature=RESPONSE_TEMPERATURE,
        max_tokens=512,
    )

    # Clean up any stray formatting the LLM might add
    cleaned = response.strip().strip('"')

    logger.info(f"Generated response: {cleaned[:100]}...")
    return cleaned
