# 🚀 AI Support Engine (v3)

> An enterprise-ready SaaS backend that automates tier-1 customer support triage. Features intelligent multi-path routing, confidence-based escalation, and deterministic business rules exposed via a robust REST API.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter_(Auto_Routing)-6366F1)](https://openrouter.ai)

---

## ⚡ Quick Start

```bash
# 1. Setup Environment
python -m venv venv
venv\Scripts\activate              # Windows
pip install -r requirements.txt

# 2. Configure API key
copy .env.example .env
# Edit .env → set OPENROUTER_API_KEY=sk-or-v1-xxxxx

# 3. Start the Inference Server
python -m uvicorn server:app --reload --port 8000
```

---

## 📋 Table of Contents

- [The Product](#-the-product)
- [API Integration](#-api-integration)
- [System Architecture](#-system-architecture)
- [Advanced Robustness](#-advanced-robustness)
- [Rule-Based Priority Engine](#-rule-based-priority-engine)
- [CLI Fallback](#-cli-fallback)

---

## 🎯 The Product

Customer support queues are bottlenecks that scale linearly with user growth. This engine acts as an automated triage layer that:

1. **Classifies** incoming tickets with an AI confidence score.
2. **Extracts** structured metadata (Order IDs, sentiment).
3. **Prioritizes** tickets using deterministic business rules.
4. **Routes** them to specialized AI workflows (e.g., Refund vs. Complaint).
5. **Escalates** low-confidence or high-risk tickets directly to humans.

This is **not a chatbot**. It is an automated inference pipeline designed to integrate seamlessly with existing CRM systems (like Zendesk or Intercom) via webhooks.

---

## 🔌 API Integration

The system exposes a FastAPI REST layer for immediate integration into an event-driven architecture.

### Health Check
Ensure the inference server is responsive.
```bash
curl -X GET http://localhost:8000/health
```
```json
{"status": "ok"}
```

### Process Single Webhook
Post a customer message to the pipeline in real-time.
```bash
curl -X POST http://localhost:8000/process-message \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a refund for order #9982. It arrived shattered."}'
```
```json
{
  "category": "Refund Request",
  "priority": "High",
  "sentiment": "Negative",
  "order_id": "#9982",
  "response": "[SYSTEM NOTE FOR AI]: This is a Refund Request workflow..."
}
```

### Process Batch Workloads
Ideal for nightly cron jobs or bulk historical analysis.
```bash
curl -X POST http://localhost:8000/process-batch \
  -H "Content-Type: application/json" \
  -d '{"messages": ["Where is my package?", "Does this come in blue?"]}'
```

---

## ⚙️ System Architecture

```
         Webhook / Event            (FastAPI Layer)
                 │
                 ▼
       ┌─────────────────────┐
       │    ORCHESTRATOR     │  ← Controls flow, retries, validation
       ├─────────────────────┤
       │                     │
       │  Step 1: CLASSIFY   │ → AI (LLM) → {"category": "Refund", "confidence": 0.95}
       │         │           │
       │  Step 2: VALIDATE   │ → if confidence < 0.70 ───▶ Escalate to Human Queue
       │         │           │
       │  Step 3: EXTRACT    │ → AI (LLM) → {order_id, sentiment}
       │         │           │
       │  Step 4: PRIORITY   │ → Rules Engine (NO AI) → "High"
       │         │           │
       │  Step 5: ROUTE      │ → Multi-Path Workflows ─┬─▶ Refund Workflow
       │                     │                         ├─▶ Complaint Workflow
       │                     │                         └─▶ Standard Workflow
       └─────────────────────┘
```

---

## 🛡️ Advanced Robustness

This engine is built to survive the unreliability of LLM API gateways and the unpredictability of human inputs.

**1. Multi-Path Workflows (Routing Logic)**
Not all tickets need the same response logic. The engine uses the output of the classification phase to route the ticket to specialized Python functions (`refund_workflow`, `complaint_workflow`, etc).

**2. Confidence-Based Human Escalation**
LLMs hallucinate most when processing ambiguous text. The classification AI now returns a strict `confidence` float. If `confidence < 0.70`, the system aborts AI generation and returns an Escalation payload, flagging it for tier-2 human review.

**3. Retry & Validation Loops (Pydantic)**
The orchestrator implements per-step retry logic for transient API timeouts (`HTTP 429`, `502`). Furthermore, every output is validated against Pydantic schemas. If a step exhausts its max retries, a safe fallback default is injected so the pipeline never crashes.

---

## 🔧 Rule-Based Priority Engine

Priority is determined by **pure Python logic** — no AI, no API calls, no token cost.

Using AI to rank priority introduces race conditions and non-determinism into critical business logic. Instead, the extracted `Category` and `Sentiment` are mapped directly to a matrix:

| Category | Sentiment | → Priority |
|---|---|---|
| Refund Request | Negative | **High** |
| Complaint | Any | **High** |
| Shipping Delay | Negative | **High** |
| Product Question | Any | **Low** |
| Other | Positive/Neutral | **Low** |

*(Others default to **Medium**)*

---

## 🖥️ CLI Fallback

For localized testing without standing up the Uvicorn server, the original CLI functionality is maintained:

```bash
# Process a single message
python main.py --message "Where is my order #12345?"

# Process a JSON batch of messages
python main.py --batch data/sample_messages.json
```
