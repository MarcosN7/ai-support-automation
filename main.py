"""
AI Customer Support Automation System — Main Entry Point

CLI interface that orchestrates the full 3-step pipeline:
  1. Classify the customer message
  2. Extract structured data (order_id, priority, sentiment)
  3. Generate a professional support response

Supports single-message and batch-processing modes.

Usage:
  # Single message
  python main.py --message "Where is my order #12345?"

  # Batch mode (from JSON file)
  python main.py --batch data/sample_messages.json

  # Specify output format
  python main.py --batch data/sample_messages.json --output-format csv
"""

import argparse
import json
import sys
import time

from config import OUTPUT_DIR
from services.classifier import classify_message
from services.extractor import extract_data
from services.responder import generate_response
from utils.validator import validate_result, SupportTicketResult
from utils.file_handler import save_to_json, save_to_csv
from utils.logger import get_logger

logger = get_logger()


# ═══════════════════════════════════════════════════════════════════
# Pipeline
# ═══════════════════════════════════════════════════════════════════

def process_message(message: str) -> dict:
    """
    Run a single customer message through the full 3-step pipeline.

    Returns a validated result dict with keys:
      category, priority, sentiment, order_id, response
    """
    logger.info("=" * 60)
    logger.info(f"Processing message: {message[:100]}")
    logger.info("=" * 60)

    start = time.time()

    # STEP 1 — Classification
    logger.info("STEP 1: Classifying message...")
    category = classify_message(message)

    # STEP 2 — Data Extraction
    logger.info("STEP 2: Extracting structured data...")
    extracted = extract_data(message)

    # STEP 3 — Response Generation
    logger.info("STEP 3: Generating support response...")
    response_text = generate_response(message, category, extracted)

    # Assemble result
    raw_result = {
        "category": category,
        "priority": extracted["priority"],
        "sentiment": extracted["sentiment"],
        "order_id": extracted["order_id"],
        "response": response_text,
    }

    # Validate
    try:
        validated: SupportTicketResult = validate_result(raw_result)
        result = validated.model_dump()
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        logger.warning("Using raw (unvalidated) result as fallback.")
        result = raw_result

    elapsed = time.time() - start
    logger.info(f"Message processed in {elapsed:.1f}s")

    return result


def process_batch(messages: list[str]) -> list[dict]:
    """
    Process a list of customer messages sequentially.

    Returns a list of validated result dicts.
    """
    total = len(messages)
    results = []

    logger.info(f"Starting batch processing: {total} message(s)")
    batch_start = time.time()

    for idx, msg in enumerate(messages, 1):
        logger.info(f"\n[{idx}/{total}] ───────────────────────────────")
        try:
            result = process_message(msg)
            result["_input_message"] = msg  # Keep original for reference
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to process message {idx}: {e}")
            results.append({
                "category": "Other",
                "priority": "Medium",
                "sentiment": "Neutral",
                "order_id": None,
                "response": f"[ERROR] Could not process: {e}",
                "_input_message": msg,
            })

    batch_elapsed = time.time() - batch_start
    logger.info(f"\nBatch complete: {len(results)}/{total} processed in {batch_elapsed:.1f}s")
    return results


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="support-automation",
        description=(
            "AI Customer Support Automation — Classify, extract, and respond "
            "to customer support messages using an LLM (via OpenRouter)."
        ),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--message", "-m",
        type=str,
        help="A single customer support message to process.",
    )
    group.add_argument(
        "--batch", "-b",
        type=str,
        metavar="FILE",
        help="Path to a JSON file containing a list of messages.",
    )
    parser.add_argument(
        "--output-format", "-o",
        choices=["json", "csv"],
        default="json",
        help="Output file format (default: json).",
    )
    return parser


def _print_result(result: dict) -> None:
    """Pretty-print a single result to the console."""
    display = {k: v for k, v in result.items() if not k.startswith("_")}
    print("\n" + "─" * 50)
    print("  RESULT")
    print("─" * 50)
    print(json.dumps(display, indent=2, ensure_ascii=False))
    print("─" * 50)


def main():
    parser = build_parser()
    args = parser.parse_args()

    # ── Single message mode ──────────────────────────────────────
    if args.message:
        result = process_message(args.message)
        _print_result(result)

        # Save single result
        results = [result]
        if args.output_format == "csv":
            path = save_to_csv(results, OUTPUT_DIR)
        else:
            path = save_to_json(results, OUTPUT_DIR)
        print(f"\n📁 Output saved to: {path}")
        return

    # ── Batch mode ───────────────────────────────────────────────
    if args.batch:
        try:
            with open(args.batch, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error(f"Batch file not found: {args.batch}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in batch file: {e}")
            sys.exit(1)

        # Support both list-of-strings and list-of-objects with "message" key
        if isinstance(data, list):
            messages = []
            for item in data:
                if isinstance(item, str):
                    messages.append(item)
                elif isinstance(item, dict) and "message" in item:
                    messages.append(item["message"])
                else:
                    logger.warning(f"Skipping unrecognized item: {item}")
        else:
            logger.error("Batch file must contain a JSON array.")
            sys.exit(1)

        if not messages:
            logger.error("No messages found in batch file.")
            sys.exit(1)

        results = process_batch(messages)

        # Print summary
        print(f"\n{'═' * 50}")
        print(f"  BATCH SUMMARY: {len(results)} messages processed")
        print(f"{'═' * 50}")
        for i, r in enumerate(results, 1):
            category = r.get("category", "?")
            priority = r.get("priority", "?")
            sentiment = r.get("sentiment", "?")
            order_id = r.get("order_id", "N/A") or "N/A"
            print(f"  [{i}] {category:<18} | {priority:<6} | {sentiment:<8} | Order: {order_id}")
        print(f"{'═' * 50}")

        # Save results
        if args.output_format == "csv":
            path = save_to_csv(results, OUTPUT_DIR)
        else:
            path = save_to_json(results, OUTPUT_DIR)
        print(f"\n📁 Output saved to: {path}")


if __name__ == "__main__":
    main()
