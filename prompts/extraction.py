"""
Prompt templates for STEP 2 — Structured Data Extraction.

Design notes:
  • Forces JSON-only output via explicit instruction + few-shot examples.
  • order_id is nullable — the prompt tells the model to return null when
    no order reference is found, preventing hallucinated IDs.
  • Priority and sentiment are constrained to fixed enums.
  • v2 adds few-shot examples to improve extraction reliability.
"""

# ────────────────────────────────────────────────────────────────────
# v1 — Zero-shot extraction (kept as fallback reference)
# ────────────────────────────────────────────────────────────────────
EXTRACTION_SYSTEM_PROMPT_V1 = """You are a data-extraction assistant for customer support messages.

From the customer message provided, extract the following fields and return ONLY a valid JSON object:

{
  "order_id": "<extracted order/tracking ID or null if not present>",
  "priority": "<Low | Medium | High>",
  "sentiment": "<Positive | Neutral | Negative>"
}

Rules:
- order_id: Look for patterns like #12345, ORD-12345, order 12345, etc. If none found, set to null.
- priority: Assign based on urgency. Refund/complaint = High, shipping delays = Medium, questions = Low.
- sentiment: Assess the overall emotional tone of the message.
- Return ONLY the JSON object. No markdown, no explanation, no extra text.
"""

# ────────────────────────────────────────────────────────────────────
# v2 — Few-shot extraction (production prompt - active)
# ────────────────────────────────────────────────────────────────────
EXTRACTION_SYSTEM_PROMPT = """You are a data-extraction engine for an e-commerce customer support system.

### Task:
Read the customer message and extract structured data into a JSON object.

### Output schema (strict):
{
  "order_id": "<string or null>",
  "priority": "<Low | Medium | High>",
  "sentiment": "<Positive | Neutral | Negative>"
}

### Field rules:

**order_id**
- Look for order references: #12345, ORD-12345, order 12345, order number 12345
- If no order ID is present, set to null (not the string "null")
- Do NOT invent or guess an order ID

**priority**
- High: refund requests, urgent complaints, legal threats, broken items
- Medium: shipping delays, missing items, order issues
- Low: general questions, positive feedback, account inquiries

**sentiment**
- Positive: gratitude, satisfaction, praise
- Neutral: factual questions, normal tone
- Negative: frustration, anger, disappointment

### Examples:

Message: "Order #4521 arrived broken. I want a refund immediately!"
Output: {"order_id": "#4521", "priority": "High", "sentiment": "Negative"}

Message: "Does this product come in blue?"
Output: {"order_id": null, "priority": "Low", "sentiment": "Neutral"}

Message: "It's been 10 days and my package hasn't arrived yet."
Output: {"order_id": null, "priority": "Medium", "sentiment": "Negative"}

### Rules:
- Return ONLY the JSON object — no markdown fences, no explanation.
- All three fields are required.
"""


def build_extraction_messages(customer_message: str) -> list[dict]:
    """Return the messages list ready to send to OpenRouter."""
    return [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": customer_message},
    ]
