import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from app.services.matcher import MatcherService
from app.models.domain import Payment, Settlement

@pytest.fixture
def mock_db():
    db = Mock()
    db.query.return_value.filter.return_value.all.return_value = []
    return db

def test_exact_reference_match(mock_db):
    matcher = MatcherService(mock_db)
    
    p = Payment(id="P-1", amount=1000, captured_at=datetime.now())
    s = Settlement(id="S-1", amount=980, fees=20, tax=0, payment_references=["P-1"])
    
    result = matcher._match_settlement(s, [p])
    
    assert result is not None
    assert result.match_type == "EXACT_MATCH"
    assert result.status == "RESOLVED"

def test_amount_mismatch_on_exact_reference(mock_db):
    matcher = MatcherService(mock_db)
    
    p = Payment(id="P-1", amount=1000, captured_at=datetime.now())
    # Settlement amount 950 (expected 980)
    s = Settlement(id="S-1", amount=950, fees=20, tax=0, payment_references=["P-1"])
    
    result = matcher._match_settlement(s, [p])
    
    assert result is not None
    assert result.match_type == "CANDIDATE_MATCH"
    assert result.status == "EXCEPTION"
    assert "amount mismatch" in result.reason.lower()

def test_deterministic_match_no_reference(mock_db):
    matcher = MatcherService(mock_db)
    
    p = Payment(id="P-1", amount=1000, captured_at=datetime.now())
    s = Settlement(id="S-1", amount=980, fees=20, tax=0, payment_references=None, settled_at=datetime.now() + timedelta(days=2))
    
    result = matcher._match_settlement(s, [p])
    
    assert result is not None
    assert result.match_type == "DETERMINISTIC_MATCH"
    assert result.status == "RESOLVED"

def test_no_match(mock_db):
    matcher = MatcherService(mock_db)
    
    p = Payment(id="P-1", amount=1000, captured_at=datetime.now())
    s = Settlement(id="S-1", amount=500, fees=10, tax=0, payment_references=None, settled_at=datetime.now())
    
    result = matcher._match_settlement(s, [p])
    
    assert result is None
