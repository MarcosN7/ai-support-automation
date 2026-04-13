"""
Structured logging for the AI Customer Support Automation System.

Provides a pre-configured logger that writes to both the console and a
rotating log file.  Every API call, input message, and output result
is logged so the system is fully auditable.
"""

import logging
import os
from datetime import datetime


def get_logger(name: str = "support_automation") -> logging.Logger:
    """
    Return a configured logger instance.

    - Console handler: INFO level, human-readable format.
    - File handler:    DEBUG level, written to logs/support_YYYY-MM-DD.log.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── Console handler ──────────────────────────────────────────
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console_fmt = logging.Formatter(
        "%(asctime)s │ %(levelname)-7s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    console.setFormatter(console_fmt)
    logger.addHandler(console)

    # ── File handler ─────────────────────────────────────────────
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"support_{today}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s │ %(levelname)-7s │ %(name)s │ %(funcName)s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    return logger
