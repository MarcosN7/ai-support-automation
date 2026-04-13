"""
Prompt templates for STEP 3 — Response Generation.

Design notes:
  • The response prompt receives full context from Steps 1 & 2 so the LLM
    can craft a reply that acknowledges the specific issue.
  • Tone guidelines ensure consistency: helpful, empathetic, professional.
  • Temperature is slightly higher (0.4) to allow natural-sounding language
    while still remaining deterministic enough for production use.
  • The model is explicitly told NOT to make promises about timelines or
    refund amounts — a key guardrail for real-world support.
"""

RESPONSE_SYSTEM_PROMPT = """You are a senior customer support representative for an e-commerce company.

### Your persona:
- Name: Support Team
- Tone: warm, professional, empathetic, and concise
- You speak like a real human — not robotic or overly formal

### Guidelines:
1. Acknowledge the customer's concern directly.
2. If an order ID was provided, reference it in your reply.
3. Provide a clear next step or reassurance.
4. Keep the response between 2-4 sentences — short and helpful.
5. Do NOT make specific promises about refund amounts, delivery dates, or resolution timelines.
6. Do NOT use generic filler like "Thank you for reaching out" as the opening line — vary your openings.
7. End with a helpful closing that invites follow-up if needed.

### Constraints:
- Do NOT output JSON — respond with plain text only.
- Do NOT include any metadata, labels, or prefixes.
- Return ONLY the customer-facing reply.
"""


def build_response_messages(
    customer_message: str,
    category: str,
    order_id: str | None,
    priority: str,
    sentiment: str,
) -> list[dict]:
    """
    Build the messages list for response generation.

    The user prompt includes the original message plus context from
    classification and extraction so the LLM can tailor its reply.
    """
    context_block = (
        f"--- INTERNAL CONTEXT (do not expose to customer) ---\n"
        f"Category: {category}\n"
        f"Order ID: {order_id or 'N/A'}\n"
        f"Priority: {priority}\n"
        f"Sentiment: {sentiment}\n"
        f"--- END CONTEXT ---\n\n"
        f"Customer message:\n{customer_message}"
    )

    return [
        {"role": "system", "content": RESPONSE_SYSTEM_PROMPT},
        {"role": "user", "content": context_block},
    ]
