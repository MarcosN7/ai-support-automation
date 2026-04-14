"""
Centralized configuration for the AI Customer Support Automation System.

Loads environment variables and defines all constants used across modules.
"""

import os
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")


def get_api_key() -> str:
    """
    Return the OpenRouter API key, raising a clear error if it's missing.

    This is called lazily (at first API call) rather than at import time
    so that CLI features like --help still work without a .env file.
    """
    key = OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "OPENROUTER_API_KEY is not set. "
            "Create a .env file with OPENROUTER_API_KEY=your_key_here "
            "or export the variable in your shell."
        )
    return key

# ---------------------------------------------------------------------------
# OpenRouter API Settings
# ---------------------------------------------------------------------------
OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL: str = "openrouter/auto"

# Request behaviour
REQUEST_TIMEOUT: int = 60          # seconds
MAX_RETRIES: int = 3
RETRY_BACKOFF_FACTOR: float = 3.0  # longer backoff for free-tier rate limits

# LLM generation parameters
CLASSIFICATION_TEMPERATURE: float = 0.1   # very deterministic
EXTRACTION_TEMPERATURE: float = 0.1
RESPONSE_TEMPERATURE: float = 0.4         # slightly more creative for replies

# ---------------------------------------------------------------------------
# Domain Constants
# ---------------------------------------------------------------------------
VALID_CATEGORIES: list[str] = [
    "Order Issue",
    "Refund Request",
    "Shipping Delay",
    "Product Question",
    "Complaint",
    "Other",
]

VALID_PRIORITIES: list[str] = ["Low", "Medium", "High"]
VALID_SENTIMENTS: list[str] = ["Positive", "Neutral", "Negative"]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_DIR: str = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR: str = os.path.join(PROJECT_DIR, "prompts")
OUTPUT_DIR: str = os.path.join(PROJECT_DIR, "output")
