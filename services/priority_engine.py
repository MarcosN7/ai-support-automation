"""
Rule-Based Priority Engine — STEP 3 of the pipeline.

Determines ticket priority using deterministic business rules.
This layer does NOT use AI — it's pure Python logic, making it:
  • 100% predictable and testable
  • Zero latency (no API calls)
  • Easy to audit and modify

The rules encode real-world support team knowledge about what
constitutes an urgent vs. routine ticket.
"""

from utils.logger import get_logger

logger = get_logger()


# ═══════════════════════════════════════════════════════════════════
# Priority Rules Matrix
# ═══════════════════════════════════════════════════════════════════
#
# Format: (category, sentiment) → priority
#
# Rules are checked top-to-bottom. First match wins.
# More specific rules come before general ones.
#
PRIORITY_RULES: list[tuple[str | None, str | None, str]] = [
    # ── HIGH priority ────────────────────────────────────────────
    # Refund requests with negative sentiment = angry customer wanting money back
    ("Refund Request",   "Negative",  "High"),
    # Any complaint = needs immediate attention
    ("Complaint",        "Negative",  "High"),
    ("Complaint",        "Neutral",   "High"),
    ("Complaint",        "Positive",  "High"),   # rare but still a complaint
    # Shipping delay + frustrated customer = escalation risk
    ("Shipping Delay",   "Negative",  "High"),

    # ── MEDIUM priority ──────────────────────────────────────────
    # Refund request but calm tone = standard process
    ("Refund Request",   "Neutral",   "Medium"),
    ("Refund Request",   "Positive",  "Medium"),
    # Order issues = need attention but not critical
    ("Order Issue",      "Negative",  "Medium"),
    ("Order Issue",      "Neutral",   "Medium"),
    ("Order Issue",      "Positive",  "Medium"),
    # Shipping delay but not upset = routine follow-up
    ("Shipping Delay",   "Neutral",   "Medium"),
    ("Shipping Delay",   "Positive",  "Medium"),

    # ── LOW priority ─────────────────────────────────────────────
    # Product questions = informational, no urgency
    ("Product Question", None,        "Low"),    # any sentiment
    # Other/positive = likely feedback or general inquiry
    ("Other",            "Positive",  "Low"),
    ("Other",            "Neutral",   "Low"),
]

# Default when no rule matches
DEFAULT_PRIORITY = "Medium"


# ═══════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════

def determine_priority(category: str, sentiment: str) -> str:
    """
    Determine ticket priority using rule-based logic.

    This function is 100% deterministic — same inputs always produce
    the same output. No AI involved.

    Args:
        category:  The classified category (e.g. "Refund Request")
        sentiment: The extracted sentiment (e.g. "Negative")

    Returns:
        Priority string: "Low", "Medium", or "High"
    """
    for rule_cat, rule_sent, priority in PRIORITY_RULES:
        # Category must match
        if rule_cat != category:
            continue
        # Sentiment: None means "any sentiment matches"
        if rule_sent is not None and rule_sent != sentiment:
            continue
        # Match found
        logger.info(
            f"Priority rule matched: ({category}, {sentiment}) -> {priority}"
        )
        return priority

    # No rule matched -- use default
    logger.warning(
        f"No priority rule for ({category}, {sentiment}) -- "
        f"defaulting to {DEFAULT_PRIORITY}"
    )
    return DEFAULT_PRIORITY
