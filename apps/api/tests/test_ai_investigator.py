import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.ai_investigator import AIInvestigatorService
from app.models.domain import ReconciliationResult, Payment, Settlement

@patch("app.services.ai_investigator.Groq")
def test_ai_investigator_auto_resolves(mock_groq_class):
    # Setup mock Groq client
    mock_client = Mock()
    mock_groq_class.return_value = mock_client
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"confidence": 0.95, "action": "AUTO_RESOLVE", "reason": "The amount difference exactly matches the known processing fee."}'
    mock_client.chat.completions.create.return_value = mock_response

    # Test data
    result = ReconciliationResult(
        source_record_id="P-1",
        candidate_record_id="S-1",
        match_type="CANDIDATE_MATCH",
        reason="Amount mismatch"
    )
    p = Payment(id="P-1", amount=1000, currency="INR", captured_at=datetime.now())
    s = Settlement(id="S-1", amount=900, fees=100, tax=0, settled_at=datetime.now(), payment_references=["P-1"])

    service = AIInvestigatorService(api_key="fake-key")
    decision = service.investigate(result, p, s)

    assert decision.confidence == 0.95
    assert decision.action == "AUTO_RESOLVE"
    assert "known processing fee" in decision.reason

@patch("app.services.ai_investigator.Groq")
def test_ai_investigator_fallback_on_bad_json(mock_groq_class):
    mock_client = Mock()
    mock_groq_class.return_value = mock_client
    
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = 'This is not valid JSON'
    mock_client.chat.completions.create.return_value = mock_response

    result = ReconciliationResult(match_type="CANDIDATE_MATCH")
    p = Payment(id="P-1", amount=1000)
    s = Settlement(id="S-1", amount=900)

    service = AIInvestigatorService(api_key="fake-key")
    decision = service.investigate(result, p, s)

    assert decision.confidence == 0.0
    assert decision.action == "ESCALATE"
    assert "Failed to parse AI response" in decision.reason
