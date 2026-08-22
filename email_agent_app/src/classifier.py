import os
from dotenv import load_dotenv
from openai import OpenAI
from src.schemas import ClassificationResult, Email, IntentCategory

load_dotenv()

SYSTEM_PROMPT = """
You are an expert Autonomous Email Classification Agent for a corporate finance team.
Classify incoming emails into one of these intents:
1. "invoice_submission"
2. "payment_query"
3. "dispute"
4. "spam"

Classification Rules:
- Analyze subject line and body content.
- Provide a confidence score between 0.0 and 1.0.
- If an email contains overlapping intents or is ambiguous, set `is_ambiguous` to true.
"""


class EmailClassifier:
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=key) if key else None
        self.model = model

    def classify(self, email: Email) -> ClassificationResult:
        if not self.client:
            return self._heuristic_fallback(email)

        user_content = f"ID: {email.id}\nSender: {email.sender}\nSubject: {email.subject}\nBody:\n{email.body}"

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                response_format=ClassificationResult,
                temperature=0.0,
            )
            return response.choices[0].message.parsed
        except Exception as e:
            return ClassificationResult(
                email_id=email.id,
                intent=IntentCategory.AMBIGUOUS,
                confidence_score=0.0,
                reasoning=f"LLM Classification failed: {str(e)}",
                is_ambiguous=True,
            )

    def _heuristic_fallback(self, email: Email) -> ClassificationResult:
        text = f"{email.subject} {email.body}".lower()

        if "gift card" in text or "congratulations" in text or ".biz" in email.sender or ".xyz" in email.sender:
            return ClassificationResult(
                email_id=email.id,
                intent=IntentCategory.SPAM,
                confidence_score=0.95,
                reasoning="Rule trigger: High-risk phishing terms detected.",
                is_ambiguous=False,
            )

        if "incorrect charge" in text or "dispute" in text or "unauthorized" in text:
            is_mixed = "invoice" in text or "attached" in text
            return ClassificationResult(
                email_id=email.id,
                intent=IntentCategory.DISPUTE,
                confidence_score=0.65 if is_mixed else 0.90,
                reasoning="Rule trigger: Dispute language detected." + (" Mixed with invoice terms." if is_mixed else ""),
                is_ambiguous=is_mixed,
            )

        if "status of payment" in text or "update on payment" in text or "payment status" in text:
            return ClassificationResult(
                email_id=email.id,
                intent=IntentCategory.PAYMENT_QUERY,
                confidence_score=0.90,
                reasoning="Rule trigger: Payment status inquiry.",
                is_ambiguous=False,
            )

        if "invoice" in text or "attached" in text:
            return ClassificationResult(
                email_id=email.id,
                intent=IntentCategory.INVOICE_SUBMISSION,
                confidence_score=0.88,
                reasoning="Rule trigger: Invoice submission terms.",
                is_ambiguous=False,
            )

        return ClassificationResult(
            email_id=email.id,
            intent=IntentCategory.AMBIGUOUS,
            confidence_score=0.40,
            reasoning="Rule trigger: Low confidence threshold.",
            is_ambiguous=True,
        )