"""
Orchestrator — controls the multi-step AI workflow.

This is the central controller that manages the full pipeline:
  Step 1: classify_message()     → AI
  Step 2: extract_data()         → AI
  Step 3: determine_priority()   → Rules (no AI)
  Step 4: generate_response()    → AI

The orchestrator handles:
  • Sequential step execution with logging
  • Per-step retry logic for AI failures
  • Validation gates between steps
  • Batch processing with per-message error isolation
  • Final output assembly and validation
"""

import time

from services.classifier import classify_message
from services.extractor import extract_data
from services.priority_engine import determine_priority
from services.responder import generate_response
from services.ai_client import OpenRouterError
from utils.validator import validate_result, SupportTicketResult
from utils.logger import get_logger

logger = get_logger()

# Max retries for individual AI steps within the pipeline
STEP_MAX_RETRIES = 2


# ═══════════════════════════════════════════════════════════════════
# Single Message Pipeline
# ═══════════════════════════════════════════════════════════════════

def process_message(message: str) -> dict:
    """
    Run a single customer message through the full 4-step pipeline.

    Pipeline:
      1. CLASSIFY   (AI)   → category
      2. EXTRACT    (AI)   → order_id, sentiment
      3. PRIORITY   (Rules)→ priority
      4. RESPOND    (AI)   → customer reply

    Returns a validated result dict with keys:
      category, priority, sentiment, order_id, response
    """
    logger.info("=" * 60)
    logger.info(f"ORCHESTRATOR: Processing message: {message[:100]}")
    logger.info("=" * 60)

    start = time.time()

    # ── STEP 1: Classification (AI) ──────────────────────────────
    logger.info("STEP 1/4: Classifying message...")
    category = _run_with_retry(
        step_name="classification",
        fn=lambda: classify_message(message),
        fallback="Other",
    )

    # ── STEP 2: Data Extraction (AI) ─────────────────────────────
    logger.info("STEP 2/4: Extracting structured data...")
    extracted = _run_with_retry(
        step_name="extraction",
        fn=lambda: extract_data(message),
        fallback={"order_id": None, "sentiment": "Neutral"},
    )

    order_id = extracted["order_id"]
    sentiment = extracted["sentiment"]

    # ── STEP 3: Priority Determination (Rules — NO AI) ───────────
    logger.info("STEP 3/4: Determining priority (rule engine)...")
    priority = determine_priority(category, sentiment)

    # ── STEP 4: Response Generation (AI) ─────────────────────────
    logger.info("STEP 4/4: Generating support response...")
    response_text = _run_with_retry(
        step_name="response",
        fn=lambda: generate_response(
            message, category, order_id, priority, sentiment
        ),
        fallback=(
            "We've received your message and our support team will get back "
            "to you shortly. Thank you for your patience."
        ),
    )

    # ── Assemble final output ────────────────────────────────────
    raw_result = {
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "order_id": order_id,
        "response": response_text,
    }

    # ── Validate with Pydantic ───────────────────────────────────
    try:
        validated: SupportTicketResult = validate_result(raw_result)
        result = validated.model_dump()
        logger.info("Output validation: PASSED")
    except Exception as e:
        logger.error(f"Output validation failed: {e}")
        logger.warning("Using raw (unvalidated) result as fallback.")
        result = raw_result

    elapsed = time.time() - start
    logger.info(f"Message processed in {elapsed:.1f}s")

    return result


# ═══════════════════════════════════════════════════════════════════
# Batch Processing
# ═══════════════════════════════════════════════════════════════════

def process_batch(messages: list[str]) -> list[dict]:
    """
    Process a list of customer messages sequentially.

    Each message is processed independently — a failure in one message
    does not affect others. Failed messages get a safe error result.

    Returns a list of result dicts.
    """
    total = len(messages)
    results = []

    logger.info(f"ORCHESTRATOR: Starting batch — {total} message(s)")
    batch_start = time.time()

    for idx, msg in enumerate(messages, 1):
        logger.info(f"\n[{idx}/{total}] -------------------------------")
        try:
            result = process_message(msg)
            result["_input_message"] = msg   # Keep original for reference
            results.append(result)
        except Exception as e:
            logger.error(f"Pipeline failed for message {idx}: {e}")
            results.append({
                "category": "Other",
                "priority": "Medium",
                "sentiment": "Neutral",
                "order_id": None,
                "response": f"[ERROR] Could not process this message: {e}",
                "_input_message": msg,
            })

    batch_elapsed = time.time() - batch_start
    logger.info(
        f"\nBatch complete: {len(results)}/{total} processed "
        f"in {batch_elapsed:.1f}s"
    )
    return results


# ═══════════════════════════════════════════════════════════════════
# Internal Helpers
# ═══════════════════════════════════════════════════════════════════

def _run_with_retry(step_name: str, fn, fallback):
    """
    Execute a pipeline step with retry logic.

    If the step fails after all retries, log the error and return
    the fallback value so the pipeline continues.

    Args:
        step_name: Human-readable name for logging.
        fn:        Callable that executes the step.
        fallback:  Value to return if the step fails completely.

    Returns:
        The step result, or the fallback value on failure.
    """
    for attempt in range(1, STEP_MAX_RETRIES + 1):
        try:
            return fn()
        except OpenRouterError as e:
            logger.warning(
                f"Step '{step_name}' failed (attempt {attempt}/{STEP_MAX_RETRIES}): {e}"
            )
            if attempt == STEP_MAX_RETRIES:
                logger.error(
                    f"Step '{step_name}' exhausted all retries. "
                    f"Using fallback: {fallback}"
                )
                return fallback
        except Exception as e:
            logger.error(f"Step '{step_name}' unexpected error: {e}")
            return fallback

    return fallback
