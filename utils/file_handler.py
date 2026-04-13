"""
File I/O utilities for saving processed results.

Supports JSON and CSV output formats.  Output directory is created
automatically if it doesn't exist.
"""

import csv
import json
import os
from datetime import datetime

from utils.logger import get_logger

logger = get_logger()


def _ensure_output_dir(directory: str) -> None:
    """Create the output directory tree if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)


def _generate_filename(output_dir: str, prefix: str, extension: str) -> str:
    """Generate a timestamped filename to avoid overwrites."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{extension}"
    return os.path.join(output_dir, filename)


def save_to_json(results: list[dict], output_dir: str) -> str:
    """
    Save a list of result dicts to a timestamped JSON file.

    Returns the absolute path of the created file.
    """
    _ensure_output_dir(output_dir)
    filepath = _generate_filename(output_dir, "results", "json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to JSON: {filepath}")
    return filepath


def save_to_csv(results: list[dict], output_dir: str) -> str:
    """
    Save a list of result dicts to a timestamped CSV file.

    Returns the absolute path of the created file.
    """
    if not results:
        logger.warning("No results to save.")
        return ""

    _ensure_output_dir(output_dir)
    filepath = _generate_filename(output_dir, "results", "csv")

    fieldnames = ["category", "priority", "sentiment", "order_id", "response"]

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    logger.info(f"Results saved to CSV: {filepath}")
    return filepath
