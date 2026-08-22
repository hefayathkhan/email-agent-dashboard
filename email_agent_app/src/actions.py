from datetime import datetime, timezone
from src.schemas import AuditEntry, ClassificationResult, Email, IntentCategory


class ActionEngine:
    def execute(self, email: Email, classification: ClassificationResult) -> AuditEntry:
        if classification.is_ambiguous or classification.confidence_score < 0.70:
            return self._handle_ambiguous(email, classification)

        if classification.intent == IntentCategory.INVOICE_SUBMISSION:
            return self._handle_invoice(email, classification)
        elif classification.intent == IntentCategory.PAYMENT_QUERY:
            return self._handle_payment_query(email, classification)
        elif classification.intent == IntentCategory.DISPUTE:
            return self._handle_dispute(email, classification)
        elif classification.intent == IntentCategory.SPAM:
            return self._handle_spam(email, classification)
        else:
            return self._handle_ambiguous(email, classification)

    def _handle_invoice(self, email: Email, classification: ClassificationResult) -> AuditEntry:
        return self._create_entry(
            email, classification, "LOG_INVOICE_TO_ERP",
            f"Parsed invoice from '{email.sender}'. Created AP record.", "SUCCESS"
        )

    def _handle_payment_query(self, email: Email, classification: ClassificationResult) -> AuditEntry:
        return self._create_entry(
            email, classification, "DRAFT_STATUS_REPLY",
            f"Drafted auto-reply to '{email.sender}' with status 'In Queue'.", "SUCCESS"
        )

    def _handle_dispute(self, email: Email, classification: ClassificationResult) -> AuditEntry:
        return self._create_entry(
            email, classification, "ESCALATE_TO_FINANCE_LEAD",
            "Flagged billing dispute. Created Priority-1 ticket.", "SUCCESS"
        )

    def _handle_spam(self, email: Email, classification: ClassificationResult) -> AuditEntry:
        return self._create_entry(
            email, classification, "QUARANTINE_AND_BLOCK",
            f"Moved '{email.sender}' to quarantine.", "SUCCESS"
        )

    def _handle_ambiguous(self, email: Email, classification: ClassificationResult) -> AuditEntry:
        return self._create_entry(
            email, classification, "FLAG_FOR_HUMAN_REVIEW",
            f"Flagged due to overlapping intents/low confidence ({classification.confidence_score:.2f}).", "FLAGGED"
        )

    def _create_entry(
        self, email: Email, classification: ClassificationResult, action_taken: str, action_details: str, status: str
    ) -> AuditEntry:
        return AuditEntry(
            email_id=email.id,
            sender=email.sender,
            subject=email.subject,
            intent=classification.intent,
            confidence_score=classification.confidence_score,
            action_taken=action_taken,
            action_details=action_details,
            reasoning=classification.reasoning,
            status=status,
            processed_at=datetime.now(timezone.utc).isoformat(),
        )