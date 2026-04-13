# 🤖 AI Support Automation

> An intelligent, LLM-powered backend system that automatically classifies, analyzes, and responds to customer support messages — designed to reduce manual workload for e-commerce support teams.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-6366F1?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMkw0IDdWMTdMMTIgMjJMMjAgMTdWN0wxMiAyWiIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIi8+PC9zdmc+)](https://openrouter.ai)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ⚡ Quick Start (TL;DR)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ai-support-automation.git
cd ai-support-automation

# 2. Set up Python environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# 3. Add your OpenRouter API key
copy .env.example .env         # Windows
# cp .env.example .env         # macOS/Linux
# Edit .env → set OPENROUTER_API_KEY=sk-or-v1-xxxxx

# 4. Run it
python main.py --message "Where is my order #12345?"
```

---

## 📋 Table of Contents

- [Quick Start](#-quick-start-tldr)
- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Usage](#-usage)
- [Example Input/Output](#-example-inputoutput)
- [OpenRouter Integration](#-openrouter-integration)
- [Prompt Engineering](#-prompt-engineering)
- [Architecture Decisions](#-architecture-decisions)
- [Future Improvements](#-future-improvements)
- [License](#-license)

---

## 🎯 Problem Statement

E-commerce companies handle hundreds to thousands of customer support messages daily. Manual processing creates:

- **Slow response times** — customers wait hours or days for a reply
- **Inconsistent quality** — different agents give different answers
- **Misrouted tickets** — messages end up in the wrong queue
- **Agent burnout** — repetitive tasks reduce morale and efficiency
- **Missed insights** — sentiment and priority data isn't captured systematically

---

## 💡 Solution Overview

This system automates the first-response workflow by:

1. **Classifying** each message into a business-relevant category
2. **Extracting** structured data (order IDs, priority level, sentiment)
3. **Generating** a professional, context-aware response

All outputs are validated, logged, and saved — ready to feed into CRM systems, dashboards, or escalation workflows.

This is **not a chatbot**. It's an automated triage and response engine designed to integrate into existing support infrastructure.

---

## ⚙️ How It Works

```
┌─────────────────────────────────────────────────────────┐
│                   Customer Message                       │
│  "My order #8834 hasn't shipped in 5 days. What's       │
│   going on?"                                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   STEP 1: CLASSIFY     │
        │   → "Order Issue"      │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   STEP 2: EXTRACT      │
        │   → order_id: #8834    │
        │   → priority: Medium   │
        │   → sentiment: Negative│
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   STEP 3: RESPOND      │
        │   → Professional reply │
        │     using all context  │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   VALIDATE & SAVE      │
        │   → Pydantic schema    │
        │   → JSON / CSV output  │
        └────────────────────────┘
```

Each step uses a **separate, optimized LLM call** with its own prompt template, temperature setting, and validation logic. This architecture ensures:

- **Independent validation** — each step's output is checked before moving on
- **Easier debugging** — when something goes wrong, you know exactly which step failed
- **Prompt iteration** — you can improve one step without affecting the others

---

## 🛠 Tech Stack

| Component        | Technology                                    |
|------------------|-----------------------------------------------|
| Language         | Python 3.10+                                  |
| LLM Provider     | [OpenRouter](https://openrouter.ai/)          |
| Default Model    | `anthropic/claude-sonnet-4.6`                 |
| HTTP Client      | `requests`                                    |
| Validation       | `pydantic` v2                                 |
| Configuration    | `python-dotenv`                               |
| Output Formats   | JSON, CSV                                     |

---

## 📁 Project Structure

```
ai-support-automation/
├── main.py                    # CLI entry point (single + batch mode)
├── config.py                  # Environment variables & constants
├── requirements.txt           # Python dependencies
├── .env.example               # API key template (copy to .env)
│
├── services/                  # Core business logic
│   ├── openrouter_client.py   # Reusable OpenRouter HTTP client w/ retries
│   ├── classifier.py          # Step 1: Message classification
│   ├── extractor.py           # Step 2: Structured data extraction
│   └── responder.py           # Step 3: Response generation
│
├── prompts/                   # LLM prompt templates
│   ├── classification.py      # Classification prompts (v1 zero-shot + v2 few-shot)
│   ├── extraction.py          # Extraction prompts with JSON schema
│   └── response.py            # Response generation with persona & guardrails
│
├── utils/                     # Shared utilities
│   ├── logger.py              # Structured logging (console + daily log files)
│   ├── validator.py           # Pydantic output schema validation
│   └── file_handler.py        # JSON/CSV file I/O with timestamped filenames
│
├── data/
│   └── sample_messages.json   # 6 sample messages for testing
│
├── output/                    # Generated results (auto-created)
└── logs/                      # Daily log files (auto-created)
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
5. Add credit to your account (pay-per-token, no monthly fee)

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-support-automation.git
cd ai-support-automation

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
venv\Scripts\activate          # Windows (PowerShell/CMD)
# source venv/bin/activate     # macOS / Linux

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up your API key
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux
```

Then open `.env` in your editor and replace `your_api_key_here` with your actual OpenRouter API key:

```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

### Verify Installation

```bash
python main.py --help
```

You should see the CLI help output with available options.

---

## 📖 Usage

### Process a Single Message

```bash
python main.py --message "Where is my order #12345? It's been a week!"
```

### Batch Processing (Multiple Messages)

```bash
python main.py --batch data/sample_messages.json
```

The batch file should be a JSON array of strings:

```json
[
  "Where is my order #12345?",
  "I want a refund for order #9988.",
  "Does this product come in red?"
]
```

Or a JSON array of objects with a `"message"` key:

```json
[
  {"message": "Where is my order #12345?"},
  {"message": "I want a refund for order #9988."}
]
```

### Export as CSV

```bash
python main.py --batch data/sample_messages.json --output-format csv
```

### All Options

```
usage: support-automation [-h] (--message MESSAGE | --batch FILE)
                          [--output-format {json,csv}]

options:
  -h, --help                        Show help message
  --message MESSAGE, -m MESSAGE     Single message to process
  --batch FILE, -b FILE             JSON file with multiple messages
  --output-format {json,csv}, -o    Output format (default: json)
```

---

## 📊 Example Input/Output

### Input

```text
"I want a full refund for order #2210. The product arrived damaged and I'm extremely disappointed."
```

### Output

```json
{
  "category": "Refund Request",
  "priority": "High",
  "sentiment": "Negative",
  "order_id": "#2210",
  "response": "I completely understand your frustration — receiving a damaged product is never the experience we want for you. I've flagged order #2210 for our refund and returns team, and they'll be reviewing it as a priority. You should hear back with the next steps shortly. If you'd like, you can also reply here with photos of the damage to help speed things along."
}
```

### Batch Summary (Console Output)

```
══════════════════════════════════════════════════
  BATCH SUMMARY: 6 messages processed
══════════════════════════════════════════════════
  [1] Order Issue        | Medium | Neutral  | Order: #8834
  [2] Refund Request     | High   | Negative | Order: #2210
  [3] Shipping Delay     | Medium | Negative | Order: N/A
  [4] Product Question   | Low    | Neutral  | Order: N/A
  [5] Complaint          | High   | Negative | Order: #7751
  [6] Other              | Low    | Positive | Order: N/A
══════════════════════════════════════════════════
```

### Output Files

Results are automatically saved to the `output/` directory with timestamped filenames:

```
output/results_20260413_193512.json
output/results_20260413_194001.csv
```

---

## 🔌 OpenRouter Integration

This project uses **[OpenRouter](https://openrouter.ai/)** as the LLM gateway. OpenRouter provides:

- Access to 100+ models (Claude, GPT-4, Gemini, Llama, etc.) through a single API
- Pay-per-token pricing with no monthly commitments
- Automatic fallback and load balancing across providers

### How It's Used

All LLM calls go through a single reusable function in `services/openrouter_client.py`:

```python
def call_openrouter(messages, model, temperature, max_tokens) -> str:
    """Send a chat-completion request to OpenRouter."""
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    )
    return response.json()["choices"][0]["message"]["content"]
```

The client includes:
- **Retry logic** — 3 attempts with exponential backoff for transient failures
- **Timeout protection** — 60s per request to prevent indefinite hangs
- **Structured error handling** — for rate limits (429), server errors (5xx), and malformed responses

### Changing the Model

Edit `DEFAULT_MODEL` in `config.py` to use any model available on OpenRouter:

```python
DEFAULT_MODEL = "google/gemini-2.0-flash-001"      # Fast & cheap
DEFAULT_MODEL = "anthropic/claude-sonnet-4.6"       # Balanced (default)
DEFAULT_MODEL = "openai/gpt-4o"                     # Alternative
```

Browse all available models at [openrouter.ai/models](https://openrouter.ai/models).

---

## 🧠 Prompt Engineering

### Design Principles

1. **Separate prompts per task** — each step has its own optimized prompt
2. **Few-shot examples** — classification and extraction prompts include examples to guide output format
3. **Strict output constraints** — prompts explicitly state "return ONLY JSON" or "return ONLY the category name"
4. **Anti-hallucination guardrails** — "Do NOT invent or guess an order ID"
5. **Fallback defaults** — if the LLM returns unexpected values, the system falls back gracefully

### Prompt Versioning

Each prompt file contains both **v1** (zero-shot) and **v2** (few-shot) versions. The v2 prompts are active in production, while v1 is preserved as a reference showing the iteration process.

### Temperature Strategy

| Step           | Temperature | Rationale                          |
|----------------|-------------|------------------------------------|
| Classification | 0.1         | Near-deterministic for consistency |
| Extraction     | 0.1         | Structured data needs precision    |
| Response       | 0.4         | Natural language needs flexibility |

### Validation Layers

Even with good prompts, LLMs can produce unexpected output. The system includes multiple validation layers:

1. **JSON parsing with fallback** — handles markdown fences, partial JSON, leading/trailing text
2. **Enum validation** — categories, priorities, and sentiments are checked against allowed values
3. **Pydantic schema** — final output is validated against a strict schema before saving
4. **Safe defaults** — unrecognized values fall back to sensible defaults instead of crashing

---

## 🏗 Architecture Decisions

| Decision | Why |
|---|---|
| **3 separate LLM calls** instead of 1 | Each step can be validated independently; easier to debug and iterate on individual prompts |
| **Pydantic for validation** | Catches malformed LLM output before it reaches output files or downstream systems |
| **Reusable OpenRouter client** | Single point of change for API config; easier to swap models or add middleware |
| **CLI-first design** | Easy to integrate into cron jobs, CI/CD, or wrap with a REST API later |
| **Timestamped output files** | Prevents overwrites; creates an audit trail |
| **Lazy API key loading** | CLI `--help` works without a configured API key |

---

## 🔮 Future Improvements

### Short-term Enhancements

- **REST API wrapper** — Add a FastAPI server for real-time HTTP endpoints
- **Database storage** — Save results to PostgreSQL/Supabase for querying and analytics
- **Confidence scoring** — Track LLM confidence to flag uncertain classifications for human review
- **Multi-language support** — Detect language and respond in the customer's language

### Automation Integration

- **[n8n](https://n8n.io/)** — Open-source workflow automation to connect this system with email, Slack, Zendesk, etc.
- **[Zapier](https://zapier.com/)** — No-code integration with 5,000+ apps (Gmail, Shopify, HubSpot)
- **Webhook trigger** — Accept messages via HTTP webhook and auto-process in real-time

### Agent-Based Workflows

- **LangChain/LangGraph agents** — Build stateful agents that can look up order status, initiate refunds, or escalate to humans
- **Tool-use capabilities** — Give the LLM access to internal APIs (inventory, shipping tracker)
- **Multi-turn conversations** — Extend from single-message to threaded conversation handling
- **Human-in-the-loop** — Route high-priority/low-confidence tickets to human agents with pre-filled context

### Analytics & Monitoring

- **Sentiment trend dashboard** — Track customer sentiment over time
- **Category distribution reports** — Identify which issue types are most common
- **Response quality scoring** — A/B test different prompt versions and models
- **Cost tracking** — Monitor API spend per message and optimize model selection

---

## 📄 License

This project is for educational and demonstration purposes. MIT License.
