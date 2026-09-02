import os
import json
from pydantic import BaseModel, Field
from groq import Groq
from app.models.domain import ReconciliationResult, Payment, Settlement

class AIDecision(BaseModel):
    confidence: float = Field(..., description="A confidence score between 0.0 and 1.0.")
    action: str = Field(..., description="Must be one of: AUTO_RESOLVE, ESCALATE, REJECT.")
    reason: str = Field(..., description="A clear, evidence-based reason for this decision.")

class AIInvestigatorService:
    def __init__(self, api_key: str = None):
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY must be set to use AIInvestigatorService.")
        self.client = Groq(api_key=key)
        self.model = "openai/gpt-oss-120b"

    def investigate(self, result: ReconciliationResult, payment: Payment, settlement: Settlement) -> AIDecision:
        system_prompt = """You are an AI Finance Controller. 
Your job is to analyze ambiguous financial transactions and determine if there is enough evidence to resolve them.
Do NOT hallucinate. Use only the provided evidence.
Output a JSON object matching this exact schema:
{
    "confidence": float (must be a number between 0.0 and 1.0, e.g. 0.95),
    "action": string ("AUTO_RESOLVE" if confidence >= 0.9, "ESCALATE" if confidence >= 0.5, "REJECT" if confidence < 0.5 or high risk),
    "reason": string (explain your exact reasoning based on the evidence)
}"""

        payment_data = {
            "id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "captured_at": payment.captured_at.isoformat() if payment.captured_at else None
        }

        settlement_data = {
            "id": settlement.id,
            "amount": settlement.amount,
            "fees": settlement.fees,
            "tax": settlement.tax,
            "settled_at": settlement.settled_at.isoformat() if settlement.settled_at else None,
            "utr": settlement.utr,
            "payment_references": settlement.payment_references
        }

        evidence = f"""
Evidence:
Match Result Type: {result.match_type} (Reason: {result.reason})
Payment: {json.dumps(payment_data, indent=2)}
Settlement: {json.dumps(settlement_data, indent=2)}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": evidence}
            ],
            response_format={"type": "json_object"},
            temperature=0.1 # Keep it deterministic
        )

        response_json = response.choices[0].message.content
        try:
            decision_dict = json.loads(response_json)
            decision = AIDecision(**decision_dict)
            return decision
        except Exception as e:
            # Fallback if the model completely fails to follow instructions
            return AIDecision(
                confidence=0.0,
                action="ESCALATE",
                reason=f"Failed to parse AI response: {str(e)}. Raw response: {response_json}"
            )
