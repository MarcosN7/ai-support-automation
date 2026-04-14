"""
STEP 4 — Response Generation Service.

Generates a professional, empathetic customer support reply using
context from the classification, extraction, and priority steps.
"""

from config import RESPONSE_TEMPERATURE
from prompts.prompt_loader import load_prompt
from services.ai_client import call_llm
from utils.logger import get_logger

logger = get_logger()

# Prompt file loaded once and cached
PROMPT_FILE = "response_prompt.txt"


def generate_response(
    message: str,
    category: str,
    order_id: str | None,
    priority: str,
    sentiment: str,
) -> str:
    """
    Generate a customer-facing support reply.

    Args:
        message:   The original customer message.
        category:  Classification result from Step 1.
        order_id:  Extracted order ID from Step 2 (or None).
        priority:  Determined priority from Step 3 (rule engine).
        sentiment: Extracted sentiment from Step 2.

    Returns:
        A polished, human-sounding support reply (plain text).
    """
    logger.info(f"Generating response for category='{category}', priority='{priority}'...")

    system_prompt = load_prompt(PROMPT_FILE)

    # Build the user prompt with internal context for the LLM
    context_block = (
        f"--- INTERNAL CONTEXT (do not expose to customer) ---\n"
        f"Category: {category}\n"
        f"Order ID: {order_id or 'N/A'}\n"
        f"Priority: {priority}\n"
        f"Sentiment: {sentiment}\n"
        f"--- END CONTEXT ---\n\n"
        f"Customer message:\n{message}"
    )

    response = call_llm(
        prompt=context_block,
        system_prompt=system_prompt,
        temperature=RESPONSE_TEMPERATURE,
        max_tokens=512,
    )

    # Clean up any stray formatting the LLM might add
    cleaned = response.strip().strip('"')

    logger.info(f"Generated response: {cleaned[:100]}...")
    return cleaned
