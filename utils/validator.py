"""
Output validation for the AI Customer Support Automation System.

Uses Pydantic to enforce a strict schema on every result produced by the
LLM pipeline.  Invalid or missing fields are caught before outputs are
saved, preventing corrupted data from reaching downstream systems.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, field_validator

from config import VALID_CATEGORIES, VALID_PRIORITIES, VALID_SENTIMENTS


class SupportTicketResult(BaseModel):
    """Schema for a fully-processed customer support ticket."""

    category: str
    priority: str
    sentiment: str
    order_id: Optional[str] = None
    response: str

    # ── Validators ───────────────────────────────────────────────

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{v}'. Must be one of: {VALID_CATEGORIES}"
            )
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority '{v}'. Must be one of: {VALID_PRIORITIES}"
            )
        return v

    @field_validator("sentiment")
    @classmethod
    def validate_sentiment(cls, v: str) -> str:
        if v not in VALID_SENTIMENTS:
            raise ValueError(
                f"Invalid sentiment '{v}'. Must be one of: {VALID_SENTIMENTS}"
            )
        return v

    @field_validator("response")
    @classmethod
    def validate_response(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Response cannot be empty.")
        return v.strip()


def validate_result(data: dict) -> SupportTicketResult:
    """
    Validate a raw result dict against the SupportTicketResult schema.

    Returns a validated SupportTicketResult on success.
    Raises pydantic.ValidationError on failure.
    """
    return SupportTicketResult(**data)
