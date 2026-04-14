"""
FastAPI Server for AI Customer Support Automation.

Exposes the pipeline as a REST API to simulate a real-world integration
from external tools (e.g. Zendesk, Intercom, custom frontends).
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from services.orchestrator import process_message, process_batch
from utils.logger import get_logger

logger = get_logger()

app = FastAPI(
    title="AI Support Automation API",
    description="API for the AI-driven Customer Support triage and response engine.",
    version="3.0.0"
)

# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class SingleMessageRequest(BaseModel):
    message: str

class BatchMessageRequest(BaseModel):
    messages: List[str]

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.post("/process-message")
def api_process_message(req: SingleMessageRequest):
    """
    Process a single customer message through the AI workflow pipeline.
    """
    logger.info("API request received: POST /process-message")
    try:
        result = process_message(req.message)
        return result
    except Exception as e:
        logger.error(f"API Error in /process-message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal pipeline error processing message.")

@app.post("/process-batch")
def api_process_batch(req: BatchMessageRequest):
    """
    Process an array of messages through the AI workflow pipeline.
    """
    logger.info(f"API request received: POST /process-batch ({len(req.messages)} messages)")
    try:
        results = process_batch(req.messages)
        return {"results": results}
    except Exception as e:
        logger.error(f"API Error in /process-batch: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal pipeline error processing batch.")

# ---------------------------------------------------------------------------
# Entry Point for Uvicorn
# ---------------------------------------------------------------------------
# To run this server:
# venv\Scripts\python.exe -m uvicorn server:app --reload --port 8000
