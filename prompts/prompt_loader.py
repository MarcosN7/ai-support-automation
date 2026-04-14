"""
Prompt Loader — reads prompt templates from external .txt files.

Keeping prompts in plain text files makes them easy to edit, version,
and swap without touching Python code.
"""

import os
from functools import lru_cache

from config import PROMPTS_DIR
from utils.logger import get_logger

logger = get_logger()


@lru_cache(maxsize=16)
def load_prompt(filename: str) -> str:
    """
    Load a prompt template from the prompts/ directory.

    Results are cached so each file is read only once per process.

    Args:
        filename: Name of the .txt file (e.g. "classification_prompt.txt")

    Returns:
        The prompt text content.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    filepath = os.path.join(PROMPTS_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Prompt file not found: {filepath}. "
            f"Make sure the file exists in the prompts/ directory."
        )

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()

    logger.debug(f"Loaded prompt: {filename} ({len(content)} chars)")
    return content
