"""
Multi-path routing logic for different ticket topologies.
Demonstrates specific handling based on category.
"""

from utils.logger import get_logger
from services.responder import generate_response

logger = get_logger()

def escalate_to_human(message: str, reason: str, category: str, order_id: str | None, priority: str, sentiment: str) -> str:
    """Escalation path bypasses AI response generation because confidence is too low or system explicitly routes to humans."""
    logger.warning(f"ESCALATION TRIGGERED: {reason}. Bypassing AI responder.")
    return (
        f"[SYSTEM ESCALATION - HUMAN AGENT REQUIRED]\n"
        f"Reason: {reason}\n"
        f"We're sorry, but an automated response couldn't be generated for this request. "
        f"Your ticket has been assigned to a human agent who will reach out shortly."
    )

def refund_workflow(message: str, category: str, order_id: str | None, priority: str, sentiment: str) -> str:
    """Specific workflow routing for Refunds. Can simulate checking a DB for refund eligibility."""
    # Simulation: We could add a DB query here to check if order_id is eligible.
    logger.info("ROUTING: Executing Refund Workflow...")
    
    # We append extra context to the message to instruct the responder explicitly
    augmented_message = (
        f"{message}\n\n"
        f"[SYSTEM NOTE FOR AI]: This is a Refund Request workflow. Include standard 3-5 day refund processing times."
    )
    
    return generate_response(
        message=augmented_message,
        category=category,
        order_id=order_id,
        priority=priority,
        sentiment=sentiment
    )

def complaint_workflow(message: str, category: str, order_id: str | None, priority: str, sentiment: str) -> str:
    """Specific workflow routing for Complaints. Always escalates to tier-2 if sentiment is extremely negative."""
    logger.info("ROUTING: Executing Complaint Workflow...")
    
    # Example business logic for routing
    if sentiment == "Negative":
        return escalate_to_human(message, "Tier 2 Escalation (Negative Complaint)", category, order_id, priority, sentiment)
        
    augmented_message = (
        f"{message}\n\n"
        f"[SYSTEM NOTE FOR AI]: This is a Complaint workflow. Apologize profusely and offer a 10% discount code."
    )
    
    return generate_response(
        message=augmented_message,
        category=category,
        order_id=order_id,
        priority=priority,
        sentiment=sentiment
    )

def standard_workflow(message: str, category: str, order_id: str | None, priority: str, sentiment: str) -> str:
    """Standard workflow for Product Questions, Order Issues, Shipping Delays, etc."""
    logger.info(f"ROUTING: Executing Standard Workflow for {category}...")
    
    return generate_response(
        message=message,
        category=category,
        order_id=order_id,
        priority=priority,
        sentiment=sentiment
    )
