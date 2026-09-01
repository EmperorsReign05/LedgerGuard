import datetime
from sqlalchemy.orm import Session
from app.models.domain import Payment, Settlement, ReconciliationResult

class MatcherService:
    def __init__(self, db: Session):
        self.db = db

    def run_matching(self):
        # 1. Fetch all unreconciled settlements
        # For simplicity, a settlement is unreconciled if there's no ReconciliationResult for it
        # with status = RESOLVED. (In a real system, we'd have a status field or explicit join)
        
        reconciled_settlement_ids = [
            r[0] for r in self.db.query(ReconciliationResult.candidate_record_id).filter(
                ReconciliationResult.status == "RESOLVED"
            ).all()
        ]
        
        unreconciled_settlements = self.db.query(Settlement).filter(
            Settlement.id.notin_(reconciled_settlement_ids)
        ).all()
        
        # 2. Fetch all unreconciled payments
        reconciled_payment_ids = [
            r[0] for r in self.db.query(ReconciliationResult.source_record_id).filter(
                ReconciliationResult.status == "RESOLVED"
            ).all()
        ]
        
        unreconciled_payments = self.db.query(Payment).filter(
            Payment.id.notin_(reconciled_payment_ids)
        ).all()

        results = []

        for settlement in unreconciled_settlements:
            match = self._match_settlement(settlement, unreconciled_payments)
            if match:
                results.append(match)
                self.db.add(match)
                # Remove from unreconciled list so we don't double-match
                unreconciled_payments = [p for p in unreconciled_payments if p.id != match.source_record_id]
            else:
                # Log as UNRESOLVED exception
                exc = ReconciliationResult(
                    source_record_id=None,
                    candidate_record_id=settlement.id,
                    match_type="NONE",
                    match_score=0.0,
                    status="UNRESOLVED",
                    reason="No deterministic match found"
                )
                results.append(exc)
                self.db.add(exc)
                
        self.db.commit()
        return results

    def _match_settlement(self, settlement: Settlement, payments: list[Payment]) -> ReconciliationResult:
        # Rule 1: Exact Reference Match
        if settlement.payment_references:
            for p_id in settlement.payment_references:
                for payment in payments:
                    if payment.id == p_id:
                        # Check amount matches (gross amount vs net amount)
                        expected_settlement_amount = payment.amount - settlement.fees - settlement.tax
                        if settlement.amount == expected_settlement_amount:
                            return ReconciliationResult(
                                source_record_id=payment.id,
                                candidate_record_id=settlement.id,
                                match_type="EXACT_MATCH",
                                match_score=1.0,
                                status="RESOLVED",
                                reason="Exact reference and amount match"
                            )
                        else:
                            # Candidate match with amount mismatch
                            return ReconciliationResult(
                                source_record_id=payment.id,
                                candidate_record_id=settlement.id,
                                match_type="CANDIDATE_MATCH",
                                match_score=0.8,
                                status="EXCEPTION",
                                reason="Reference matched but amount mismatch"
                            )

        # Rule 2: Timestamp and Net Amount (No explicit reference)
        # Often, UTR isn't available on payment yet, but amounts and times align closely
        for payment in payments:
            expected_settlement_amount = payment.amount - settlement.fees - settlement.tax
            if settlement.amount == expected_settlement_amount:
                # Check timestamp drift
                # Assuming timezone-aware datetimes
                time_diff = abs((settlement.settled_at - payment.captured_at).total_seconds())
                if time_diff < 7 * 24 * 3600: # Within 7 days
                    return ReconciliationResult(
                        source_record_id=payment.id,
                        candidate_record_id=settlement.id,
                        match_type="DETERMINISTIC_MATCH",
                        match_score=0.9,
                        status="RESOLVED",
                        reason="Amount and timestamp within acceptable drift matched"
                    )
        
        return None
