"""
AI Customer Support Automation System — Main Entry Point (v2)

CLI interface that delegates to the orchestrator for pipeline execution.

The orchestrator runs a 4-step workflow:
  1. Classify the customer message (AI)
  2. Extract structured data — order_id + sentiment (AI)
  3. Determine priority using business rules (NO AI)
  4. Generate a professional support response (AI)

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

from config import OUTPUT_DIR
from services.orchestrator import process_message, process_batch
from utils.file_handler import save_to_json, save_to_csv
from utils.logger import get_logger

logger = get_logger()


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="support-automation",
        description=(
            "AI Customer Support Automation — Classify, extract, prioritize, "
            "and respond to customer support messages using an LLM (via OpenRouter) "
            "combined with rule-based business logic."
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
    print("\n" + "-" * 50)
    print("  RESULT")
    print("-" * 50)
    print(json.dumps(display, indent=2, ensure_ascii=False))
    print("-" * 50)


def _print_batch_summary(results: list[dict]) -> None:
    """Print a formatted batch summary table."""
    print(f"\n{'=' * 60}")
    print(f"  BATCH SUMMARY: {len(results)} messages processed")
    print(f"{'=' * 60}")
    for i, r in enumerate(results, 1):
        category = r.get("category", "?")
        priority = r.get("priority", "?")
        sentiment = r.get("sentiment", "?")
        order_id = r.get("order_id", "N/A") or "N/A"
        print(
            f"  [{i}] {category:<18} | {priority:<6} | "
            f"{sentiment:<8} | Order: {order_id}"
        )
    print(f"{'=' * 60}")


def _save_results(results: list[dict], output_format: str) -> str:
    """Save results to file and return the filepath."""
    if output_format == "csv":
        return save_to_csv(results, OUTPUT_DIR)
    return save_to_json(results, OUTPUT_DIR)


def main():
    parser = build_parser()
    args = parser.parse_args()

    # ── Single message mode ──────────────────────────────────────
    if args.message:
        result = process_message(args.message)
        _print_result(result)

        path = _save_results([result], args.output_format)
        print(f"\n[+] Output saved to: {path}")
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
        _print_batch_summary(results)

        path = _save_results(results, args.output_format)
        print(f"\n[+] Output saved to: {path}")


if __name__ == "__main__":
    main()
