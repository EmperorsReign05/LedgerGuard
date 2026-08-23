import pytest
from app.models.domain import Payment, Settlement, Refund, BankRecord, ReconciliationResult, InvestigationCase, AuditEvent

def test_models_can_be_instantiated():
    """Verify that all core financial models can be instantiated."""
    p = Payment(id="P-123", amount=1000)
    assert p.id == "P-123"
    
    s = Settlement(id="S-123", amount=980)
    assert s.id == "S-123"
    
    r = Refund(id="R-123", payment_id="P-123", amount=1000)
    assert r.amount == 1000
    
    b = BankRecord(id="B-123", amount=980)
    assert b.id == "B-123"
    
    rr = ReconciliationResult(source_record_id="P-123", candidate_record_id="S-123", match_type="EXACT_MATCH", status="RESOLVED")
    assert rr.status == "RESOLVED"
    
    ic = InvestigationCase(id="C-123", case_type="AMOUNT_MISMATCH", status="OPEN", evidence={"test": "data"})
    assert ic.case_type == "AMOUNT_MISMATCH"
    
    ae = AuditEvent(entity_type="INVESTIGATION_CASE", entity_id="C-123", action="AUTO_RESOLVE", actor="SYSTEM")
    assert ae.actor == "SYSTEM"
