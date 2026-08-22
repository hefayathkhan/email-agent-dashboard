from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class IntentCategory(str, Enum):
    INVOICE_SUBMISSION = "invoice_submission"
    PAYMENT_QUERY = "payment_query"
    DISPUTE = "dispute"
    SPAM = "spam"
    AMBIGUOUS = "ambiguous"


class Email(BaseModel):
    id: str
    sender: str
    subject: str
    timestamp: str
    body: str


class ClassificationResult(BaseModel):
    email_id: str
    intent: IntentCategory
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0"
    )
    reasoning: str = Field(..., description="Explanation of why this intent was selected")
    is_ambiguous: bool = Field(
        default=False, description="Flagged if multiple intents overlap or confidence is low"
    )


class AuditEntry(BaseModel):
    email_id: str
    sender: str
    subject: str
    intent: IntentCategory
    confidence_score: float
    action_taken: str
    action_details: str
    reasoning: str
    status: str = "SUCCESS"
    processed_at: str