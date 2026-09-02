from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import SessionLocal, engine, Base
from app.models.domain import ReconciliationResult, Payment, Settlement
from app.services.matcher import MatcherService
from app.services.ai_investigator import AIInvestigatorService

app = FastAPI(title="LedgerGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "LedgerGuard API"}

@app.get("/api/results")
def get_results(db: Session = Depends(get_db)):
    results = db.query(ReconciliationResult).order_by(
        # Put exceptions and unresolved first
        desc(ReconciliationResult.status == 'EXCEPTION'),
        desc(ReconciliationResult.status == 'UNRESOLVED'),
        ReconciliationResult.id
    ).all()
    
    output = []
    for r in results:
        payment = None
        settlement = None
        if r.source_record_id:
            p = db.query(Payment).filter(Payment.id == r.source_record_id).first()
            if p:
                payment = {"id": p.id, "amount": p.amount, "currency": p.currency, "status": p.status}
        if r.candidate_record_id:
            s = db.query(Settlement).filter(Settlement.id == r.candidate_record_id).first()
            if s:
                settlement = {"id": s.id, "amount": s.amount, "utr": s.utr, "status": s.status}
                
        output.append({
            "id": r.id,
            "status": r.status,
            "match_type": r.match_type,
            "match_score": r.match_score,
            "reason": r.reason,
            "payment": payment,
            "settlement": settlement
        })
        
    return output

@app.post("/api/run-matching")
def run_matching(db: Session = Depends(get_db)):
    # 1. Run deterministic matcher
    matcher = MatcherService(db)
    results = matcher.run_matching()
    
    # 2. Run AI Investigator on CANDIDATE_MATCH and UNRESOLVED
    ai_service = AIInvestigatorService()
    
    # Re-fetch from DB to get the latest state
    unresolved_results = db.query(ReconciliationResult).filter(
        ReconciliationResult.status.in_(["EXCEPTION", "UNRESOLVED"])
    ).all()
    
    ai_decisions_made = 0
    for r in unresolved_results:
        if r.source_record_id and r.candidate_record_id:
            payment = db.query(Payment).filter(Payment.id == r.source_record_id).first()
            settlement = db.query(Settlement).filter(Settlement.id == r.candidate_record_id).first()
            
            if payment and settlement:
                try:
                    decision = ai_service.investigate(r, payment, settlement)
                    ai_decisions_made += 1
                    
                    # Append AI reason to the existing reason
                    r.reason = f"AI [{decision.action}]: {decision.reason} (Confidence: {decision.confidence})"
                    
                    if decision.action == "AUTO_RESOLVE":
                        r.status = "RESOLVED"
                    elif decision.action == "REJECT":
                        r.status = "EXCEPTION"
                except Exception as e:
                    r.reason = f"AI [ERROR]: Failed to investigate - {str(e)}"
                    r.status = "EXCEPTION"
                    
    db.commit()
    
    return {
        "status": "success", 
        "deterministic_matches": len(results),
        "ai_investigations": ai_decisions_made
    }
