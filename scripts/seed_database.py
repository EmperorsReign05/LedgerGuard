import os
import sys
import json
import argparse
from datetime import datetime

# Add `apps/api` to sys.path so that absolute imports like `from app...` work
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "api"))

from app.db.database import SessionLocal, Base, engine
from app.models.domain import Payment, Settlement, Refund

def seed_database(json_path):
    # Ensure tables exist (we rely on alembic mostly, but just in case)
    Base.metadata.create_all(bind=engine)
    
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Refund).delete()
        db.query(Payment).delete()
        db.query(Settlement).delete()
        db.commit()

        # Insert Payments
        for p in data.get("payments", []):
            db.add(Payment(
                id=p["id"],
                amount=p["amount"],
                currency=p["currency"],
                status=p["status"],
                captured_at=datetime.fromisoformat(p["captured_at"]),
                metadata_=p.get("metadata")
            ))
            
        # Insert Settlements
        for s in data.get("settlements", []):
            db.add(Settlement(
                id=s["id"],
                amount=s["amount"],
                currency=s.get("currency", "INR"),
                fees=s["fees"],
                tax=s["tax"],
                utr=s.get("utr"),
                status=s["status"],
                settled_at=datetime.fromisoformat(s["settled_at"]),
                payment_references=s.get("payment_references")
            ))
            
        # Insert Refunds (if any)
        for r in data.get("refunds", []):
            db.add(Refund(
                id=r["id"],
                payment_id=r["payment_id"],
                amount=r["amount"],
                status=r["status"],
                created_at=datetime.fromisoformat(r["created_at"]) if "created_at" in r else datetime.now()
            ))
            
        db.commit()
        print(f"Successfully seeded database with {len(data.get('payments', []))} payments and {len(data.get('settlements', []))} settlements.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database from generated JSON dataset.")
    parser.add_argument("--file", type=str, required=True, help="Path to the JSON dataset file.")
    args = parser.parse_args()
    
    seed_database(args.file)
