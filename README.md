# 🤖 AI Support Automation

> A production-style AI workflow engine that automatically classifies, analyzes, prioritizes, and responds to customer support messages — combining LLM intelligence with deterministic business rules.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter_(Free)-6366F1)](https://openrouter.ai)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ⚡ Quick Start

```bash
# Clone
git clone https://github.com/MarcosN7/ai-support-automation.git
cd ai-support-automation

# Setup
python -m venv venv
venv\Scripts\activate              # Windows
# source venv/bin/activate         # macOS/Linux
pip install -r requirements.txt

# Configure API key
copy .env.example .env             # Windows  (cp on macOS/Linux)
# Edit .env → set OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Run
python main.py --message "Where is my order #12345?"
```

---

## 📋 Table of Contents

- [Problem](#-problem)
- [Solution](#-solution)
- [System Architecture](#-system-architecture)
- [Rule-Based Priority Engine](#-rule-based-priority-engine)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Usage](#-usage)
- [Example Input/Output](#-example-inputoutput)
- [OpenRouter Integration](#-openrouter-integration)
- [Prompt Engineering](#-prompt-engineering)
- [Future Improvements](#-future-improvements)

---

## 🎯 Problem

E-commerce support teams handle hundreds of messages daily. Manual processing creates:

- **Slow response times** — customers wait hours or days
- **Inconsistent quality** — different agents give different answers
- **Misrouted tickets** — messages end up in the wrong queue
- **No structured data** — sentiment and priority aren't captured
- **Agent burnout** — repetitive work reduces morale

---

## 💡 Solution

A **multi-step AI workflow** that automates the entire first-response pipeline:

1. **AI classifies** each message into a business category
2. **AI extracts** structured data (order IDs, sentiment)
3. **Rules determine** priority using deterministic business logic (no AI)
4. **AI generates** a professional, context-aware response

This is **not a chatbot**. It's an **automated triage and response engine** — an internal tool designed to plug into existing support infrastructure.

### Why AI + Rules?

| Layer | What it does | Why |
|---|---|---|
| **AI (LLM)** | Classification, extraction, response generation | Handles the nuance of natural language |
| **Rules Engine** | Priority determination | 100% predictable, auditable, zero-cost, instant |

Using AI for everything is expensive and unpredictable. The hybrid approach gives you the best of both worlds — intelligence where you need it and determinism where you don't.

---

## ⚙️ System Architecture

```
                    Customer Message
                          │
                          ▼
               ┌─────────────────────┐
               │    ORCHESTRATOR     │  ← controls flow, retries, validation
               ├─────────────────────┤
               │                     │
               │  Step 1: CLASSIFY   │ → AI (LLM) → "Refund Request"
               │         │          │
               │  Step 2: EXTRACT    │ → AI (LLM) → {order_id, sentiment}
               │         │          │
               │  Step 3: PRIORITY   │ → Rules Engine (NO AI) → "High"
               │         │          │
               │  Step 4: RESPOND    │ → AI (LLM) → customer reply
               │         │          │
               │  ───── VALIDATE ────│ → Pydantic schema check
               │         │          │
               │  ────── SAVE ──────│ → JSON / CSV file
               └─────────────────────┘
```

### Orchestrator Features

- **Sequential step execution** with structured logging
- **Per-step retry logic** — if an AI step fails, it retries before using fallback
- **Validation gates** — output is validated with Pydantic before saving
- **Error isolation** — in batch mode, one failed message doesn't stop the rest
- **Fallback values** — if all retries fail, the pipeline continues with safe defaults

---

## 🔧 Rule-Based Priority Engine

Priority is determined by **pure Python logic** — no AI, no API calls, no cost.

### Rules Matrix

| Category | Sentiment | → Priority |
|---|---|---|
| Refund Request | Negative | **High** |
| Complaint | Any | **High** |
| Shipping Delay | Negative | **High** |
| Refund Request | Neutral/Positive | Medium |
| Order Issue | Any | Medium |
| Shipping Delay | Neutral/Positive | Medium |
| Product Question | Any | **Low** |
| Other | Positive/Neutral | **Low** |

### Why Rules?

- ✅ **100% deterministic** — same inputs always produce the same output
- ✅ **Zero latency** — no API call needed
- ✅ **Free** — no token cost
- ✅ **Auditable** — you can explain exactly why a ticket got its priority
- ✅ **Testable** — easy to write unit tests for

The rules live in `services/priority_engine.py` and can be updated without touching any AI prompts.

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| LLM Provider | [OpenRouter](https://openrouter.ai/) (free tier) |
| Default Model | `openrouter/auto` |
| HTTP Client | `requests` |
| Validation | `pydantic` v2 |
| Config | `python-dotenv` |
| Output | JSON, CSV |
| Priority Logic | Pure Python rules engine |

---

## 📁 Project Structure

```
ai-support-automation/
├── main.py                         # CLI entry point
├── config.py                       # Environment variables & constants
├── requirements.txt                # Python dependencies
├── .env.example                    # API key template
│
├── services/                       # Core business logic
│   ├── ai_client.py                # OpenRouter HTTP client (call_llm + call_openrouter)
│   ├── classifier.py               # Step 1: Message classification (AI)
│   ├── extractor.py                # Step 2: Data extraction (AI)
│   ├── priority_engine.py          # Step 3: Rule-based priority (NO AI)
│   ├── responder.py                # Step 4: Response generation (AI)
│   └── orchestrator.py             # Pipeline controller with retries
│
├── prompts/                        # External prompt templates
│   ├── classification_prompt.txt   # Classification prompt (few-shot)
│   ├── extraction_prompt.txt       # Extraction prompt (JSON schema)
│   ├── response_prompt.txt         # Response prompt (persona + guardrails)
│   └── prompt_loader.py            # Reads .txt files with caching
│
├── utils/                          # Shared utilities
│   ├── logger.py                   # Structured logging (console + daily files)
│   ├── validator.py                # Pydantic output schema validation
│   └── file_handler.py             # JSON/CSV file I/O
│
├── data/
│   └── sample_messages.json        # 6 sample messages for testing
│
├── output/                         # Generated results (auto-created)
└── logs/                           # Daily log files (auto-created)
```

---

## 🚀 Setup & Installation

### Prerequisites

- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
- **OpenRouter API key** — [Get one here](https://openrouter.ai/keys) (free tier available)

### Getting an OpenRouter API Key

1. Go to [openrouter.ai](https://openrouter.ai/) and create an account
2. Navigate to [API Keys](https://openrouter.ai/keys)
3. Click **"Create Key"**
4. Copy the key (starts with `sk-or-v1-...`)
5. The default model (`openrouter/auto`) is free — no payment required

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/MarcosN7/ai-support-automation.git
cd ai-support-automation

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure your API key
copy .env.example .env           # Windows
# cp .env.example .env           # macOS / Linux
```

Open `.env` and set your key:

```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

### Verify

```bash
python main.py --help
```

---

## 📖 Usage

### Single Message

```bash
python main.py --message "Where is my order #12345? It's been a week!"
```

### Batch Processing

```bash
python main.py --batch data/sample_messages.json
```

### CSV Output

```bash
python main.py --batch data/sample_messages.json --output-format csv
```

### Batch File Format

JSON array of strings:

```json
[
  "Where is my order #12345?",
  "I want a refund for order #9988.",
  "Does this product come in red?"
]
```

Or objects with a `"message"` key:

```json
[
  {"message": "Where is my order #12345?"},
  {"message": "I want a refund for order #9988."}
]
```

---

## 📊 Example Input/Output

### Input

```
"I want a full refund for order #2210. The product arrived damaged and I'm extremely disappointed."
```

### Output

```json
{
  "category": "Refund Request",
  "priority": "High",
  "sentiment": "Negative",
  "order_id": "#2210",
  "response": "I'm really sorry to hear your order arrived damaged — that's absolutely not the experience we want for you. I've flagged order #2210 for our refund and returns team, and they'll be reviewing it as a priority. You can also send photos of the damage to help speed things along."
}
```

### How Priority Was Determined

```
category = "Refund Request"  +  sentiment = "Negative"
                    ↓
        Rule: (Refund Request, Negative) → High
                    ↓
            priority = "High"    ← No AI used
```

### Batch Summary

```
════════════════════════════════════════════════════════════
  BATCH SUMMARY: 6 messages processed
════════════════════════════════════════════════════════════
  [1] Order Issue        | Medium | Neutral  | Order: #8834
  [2] Refund Request     | High   | Negative | Order: #2210
  [3] Shipping Delay     | Medium | Negative | Order: N/A
  [4] Product Question   | Low    | Neutral  | Order: N/A
  [5] Complaint          | High   | Negative | Order: #7751
  [6] Other              | Low    | Positive | Order: N/A
════════════════════════════════════════════════════════════
```

---

## 🔌 OpenRouter Integration

This project uses **[OpenRouter](https://openrouter.ai/)** as the LLM gateway with a **free-tier model**.

### How It's Used

All LLM calls go through two functions in `services/ai_client.py`:

```python
# Simple interface — for most use cases
response = call_llm(
    prompt="Customer message here",
    system_prompt="You are a classifier...",
    temperature=0.1,
)

# Full interface — for multi-message conversations
response = call_openrouter(
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
    ],
)
```

Built-in reliability:
- **3 retries** with exponential backoff at the HTTP level
- **2 retries** per pipeline step at the orchestrator level
- **60s timeout** per request
- **Fallback values** if all retries fail

### Changing the Model

Edit `config.py`:

```python
DEFAULT_MODEL = "openrouter/auto"       # Free (default)
DEFAULT_MODEL = "anthropic/claude-sonnet-4.6"          # Paid — high quality
DEFAULT_MODEL = "google/gemini-2.0-flash-001"          # Paid — fast
```

---

## 🧠 Prompt Engineering

### External Prompt Files

Prompts are stored as **plain `.txt` files** in the `prompts/` directory:

```
prompts/
├── classification_prompt.txt    # Few-shot classifier
├── extraction_prompt.txt        # JSON extraction schema
└── response_prompt.txt          # Persona + guardrails
```

This makes prompts easy to edit, version, and A/B test without touching Python code.

### Design Principles

1. **Separate prompts per task** — each step is independently optimized
2. **Few-shot examples** — guides the model toward correct output format
3. **Strict constraints** — "Return ONLY valid JSON. No explanations."
4. **Anti-hallucination** — "Do NOT invent or guess an order ID"
5. **Graceful fallbacks** — malformed output is caught and defaults are used

### Temperature Strategy

| Step | Temperature | Rationale |
|---|---|---|
| Classification | 0.1 | Near-deterministic |
| Extraction | 0.1 | Structured data needs precision |
| Response | 0.4 | Natural language needs flexibility |

---

## 🔮 Future Improvements

### Automation Integration

- **[n8n](https://n8n.io/)** — Open-source workflow automation to connect with email, Slack, Zendesk
- **[Zapier](https://zapier.com/)** — No-code integration with 5,000+ apps
- **Webhook trigger** — Accept messages via HTTP and auto-process in real-time

### API Endpoints

- **FastAPI wrapper** — Expose the pipeline as REST API endpoints
- **WebSocket support** — Real-time processing for live chat systems

### Agent-Based Workflows

- **LangChain/LangGraph** — Build stateful agents that look up order status or initiate refunds
- **Tool-use** — Give the LLM access to internal APIs (inventory, shipping tracker)
- **Human-in-the-loop** — Route low-confidence tickets to human agents

### Analytics & Monitoring

- **Sentiment dashboards** — Track customer mood over time
- **Category reports** — Identify which issues are most common
- **Cost tracking** — Monitor API spend per message and optimize model selection

---

## 📄 License

MIT License — free for educational and demonstration purposes.
