import os
import sys

# Add `apps/api` to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "api"))

from app.db.database import SessionLocal
from app.models.domain import ReconciliationResult, Payment, Settlement
from app.services.ai_investigator import AIInvestigatorService

def main():
    db = SessionLocal()
    try:
        # Find a CANDIDATE_MATCH from the database
        result = db.query(ReconciliationResult).filter(
            ReconciliationResult.match_type == "CANDIDATE_MATCH"
        ).first()

        if not result:
            print("No CANDIDATE_MATCH found in the database. Ensure matcher has been run first.")
            return

        payment = db.query(Payment).filter(Payment.id == result.source_record_id).first()
        settlement = db.query(Settlement).filter(Settlement.id == result.candidate_record_id).first()

        if not payment or not settlement:
            print("Could not find the associated payment or settlement.")
            return

        print(f"Investigating {result.reason}...")
        
        investigator = AIInvestigatorService()
        decision = investigator.investigate(result, payment, settlement)
        
        print("\n=== AI DECISION ===")
        print(f"Action:     {decision.action}")
        print(f"Confidence: {decision.confidence}")
        print(f"Reasoning:  {decision.reason}")
        print("===================\n")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
