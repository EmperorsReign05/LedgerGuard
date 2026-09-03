from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from pydantic import BaseModel

from app.db.database import SessionLocal, engine, Base
from app.models.domain import ReconciliationResult, Payment, Settlement, AuditLog
from app.services.matcher import MatcherService
from app.services.ai_investigator import AIInvestigatorService

app = FastAPI(title="LedgerGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
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
        desc(ReconciliationResult.status == 'EXCEPTION'),
        desc(ReconciliationResult.status == 'UNRESOLVED'),
        desc(ReconciliationResult.id)
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

@app.get("/api/results/{result_id}")
def get_result(result_id: int, db: Session = Depends(get_db)):
    r = db.query(ReconciliationResult).filter(ReconciliationResult.id == result_id).first()
    if not r:
        return {"error": "Not found"}
        
    payment = db.query(Payment).filter(Payment.id == r.source_record_id).first() if r.source_record_id else None
    settlement = db.query(Settlement).filter(Settlement.id == r.candidate_record_id).first() if r.candidate_record_id else None
    
    logs = db.query(AuditLog).filter(AuditLog.reconciliation_result_id == r.id).order_by(AuditLog.timestamp).all()
    
    return {
        "id": r.id,
        "status": r.status,
        "match_type": r.match_type,
        "match_score": r.match_score,
        "reason": r.reason,
        "payment": payment,
        "settlement": settlement,
        "audit_logs": [{"role": l.role, "content": l.content, "timestamp": l.timestamp} for l in logs]
    }

class ChatMessage(BaseModel):
    message: str

@app.post("/api/results/{result_id}/chat")
def chat_with_ai(result_id: int, msg: ChatMessage, db: Session = Depends(get_db)):
    # 1. Save human message
    human_log = AuditLog(reconciliation_result_id=result_id, role="user", content=msg.message)
    db.add(human_log)
    db.commit()
    
    # In Phase 3 we will hook up LangChain here, for now mock AI response
    ai_log = AuditLog(reconciliation_result_id=result_id, role="assistant", content="I am investigating your request. (Agentic workflow coming in Phase 3)")
    db.add(ai_log)
    db.commit()
    
    return {"status": "success"}

@app.get("/api/metrics")
def get_metrics(db: Session = Depends(get_db)):
    total = db.query(ReconciliationResult).count()
    resolved = db.query(ReconciliationResult).filter(ReconciliationResult.status == "RESOLVED").count()
    exceptions = db.query(ReconciliationResult).filter(ReconciliationResult.status == "EXCEPTION").count()
    unresolved = db.query(ReconciliationResult).filter(ReconciliationResult.status == "UNRESOLVED").count()
    
    # Fake a 'time saved' calculation (e.g. 5 mins per resolved exception)
    time_saved_hours = round((resolved * 5) / 60, 1)
    
    return {
        "total": total,
        "resolved": resolved,
        "exceptions": exceptions,
        "unresolved": unresolved,
        "accuracy_rate": round((resolved / total * 100) if total > 0 else 0, 1),
        "human_hours_saved": time_saved_hours
    }

def process_ai_investigations(result_ids: List[int]):
    db = SessionLocal()
    try:
        ai_service = AIInvestigatorService()
        for r_id in result_ids:
            r = db.query(ReconciliationResult).filter(ReconciliationResult.id == r_id).first()
            if not r or r.status not in ["EXCEPTION", "UNRESOLVED"]:
                continue
                
            if r.source_record_id and r.candidate_record_id:
                payment = db.query(Payment).filter(Payment.id == r.source_record_id).first()
                settlement = db.query(Settlement).filter(Settlement.id == r.candidate_record_id).first()
                
                if payment and settlement:
                    try:
                        decision = ai_service.investigate(r, payment, settlement)
                        r.reason = f"AI [{decision.action}]: {decision.reason} (Confidence: {decision.confidence})"
                        
                        if decision.action == "AUTO_RESOLVE":
                            r.status = "RESOLVED"
                        elif decision.action == "REJECT":
                            r.status = "EXCEPTION"
                        elif decision.action == "ESCALATE":
                            r.status = "UNRESOLVED"
                            
                        # Save the reasoning to Audit Log
                        db.add(AuditLog(
                            reconciliation_result_id=r.id,
                            role="assistant",
                            content=f"Decision: {decision.action}\nReasoning: {decision.reason}"
                        ))
                    except Exception as e:
                        r.reason = f"AI [ERROR]: Failed to investigate - {str(e)}"
                        r.status = "EXCEPTION"
            db.commit()
    finally:
        db.close()

@app.post("/api/run-matching")
def run_matching(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Run deterministic matcher
    matcher = MatcherService(db)
    results = matcher.run_matching()
    
    # 2. Re-fetch from DB to get the latest unresolved state
    unresolved_results = db.query(ReconciliationResult).filter(
        ReconciliationResult.status.in_(["EXCEPTION", "UNRESOLVED"])
    ).all()
    
    result_ids = [r.id for r in unresolved_results]
    
    # 3. Add background task for AI Processing
    background_tasks.add_task(process_ai_investigations, result_ids)
    
    return {
        "status": "processing", 
        "deterministic_matches": len(results),
        "ai_investigations_queued": len(result_ids)
    }
