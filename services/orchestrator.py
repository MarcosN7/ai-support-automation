"""
Orchestrator — controls the multi-step AI workflow.

This is the central controller that manages the full pipeline:
  Step 1: classify_message()     → AI (category + confidence)
  Step 2: extract_data()         → AI (order_id + sentiment)
  Step 3: determine_priority()   → Rules (no AI logic)
  Step 4: workflows / routing    → Multi-path handling

The orchestrator handles:
  • Sequential step execution with logging
  • Per-step retry logic for AI failures
  • Validation gates (escalates to human if AI confidence < 0.70)
  • Batch processing with per-message error isolation
  • Final output assembly and validation
"""

import time

from services.classifier import classify_message
from services.extractor import extract_data
from services.priority_engine import determine_priority
from services.workflows import escalate_to_human, refund_workflow, complaint_workflow, standard_workflow
from services.ai_client import OpenRouterError
from utils.validator import validate_result, SupportTicketResult
from utils.logger import get_logger

logger = get_logger()

# Max retries for individual AI steps within the pipeline
STEP_MAX_RETRIES = 2
# Escalate if classification confidence is below this
CONFIDENCE_THRESHOLD = 0.70


# ═══════════════════════════════════════════════════════════════════
# Single Message Pipeline
# ═══════════════════════════════════════════════════════════════════

def process_message(message: str) -> dict:
    """
    Run a single customer message through the full 4-step pipeline.

    Returns a validated result dict with keys:
      category, priority, sentiment, order_id, response
    """
    logger.info("=" * 60)
    logger.info(f"ORCHESTRATOR: Processing message: {message[:100]}")
    logger.info("=" * 60)

    start = time.time()

    # ── STEP 1: Classification (AI) ──────────────────────────────
    logger.info("STEP 1/4: Classifying message...")
    category, confidence = _run_with_retry(
        step_name="classification",
        fn=lambda: classify_message(message),
        fallback=("Other", 0.0),
    )
    
    # ── VALIDATION GATE: Confidence Check ────────────────────────
    if confidence < CONFIDENCE_THRESHOLD:
        logger.warning(
            f"Validation Gate: Confidence ({confidence}) is below threshold ({CONFIDENCE_THRESHOLD}). "
            f"Triggering escalation workflow."
        )
        # We still run priority logic to properly tag the escalated ticket
        priority = determine_priority(category, "Neutral")
        response_text = escalate_to_human(message, "Low Classification Confidence", category, None, priority, "Neutral")
        
        raw_result = {
            "category": category,
            "priority": priority,
            "sentiment": "Neutral",
            "order_id": None,
            "response": response_text,
        }
        return _validate_and_finish(raw_result, start)

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

    # ── STEP 4: Routing & Response Generation (AI) ───────────────
    logger.info(f"STEP 4/4: Routing to specific workflow based on category '{category}'...")
    
    def generate_routed_response():
        if category == "Refund Request":
            return refund_workflow(message, category, order_id, priority, sentiment)
        elif category == "Complaint":
            return complaint_workflow(message, category, order_id, priority, sentiment)
        else:
            return standard_workflow(message, category, order_id, priority, sentiment)

    response_text = _run_with_retry(
        step_name="response",
        fn=generate_routed_response,
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

    return _validate_and_finish(raw_result, start)


def _validate_and_finish(raw_result: dict, start_time: float) -> dict:
    """Validate with Pydantic and finalize the output dict."""
    try:
        validated: SupportTicketResult = validate_result(raw_result)
        result = validated.model_dump()
        logger.info("Output validation: PASSED")
    except Exception as e:
        logger.error(f"Output validation failed: {e}")
        logger.warning("Using raw (unvalidated) result as fallback.")
        result = raw_result

    elapsed = time.time() - start_time
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
