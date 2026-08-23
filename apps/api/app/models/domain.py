from sqlalchemy import Column, String, Integer, DateTime, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, index=True)
    amount = Column(Integer, nullable=False) # In smallest currency unit
    currency = Column(String, default="INR")
    status = Column(String, index=True)
    captured_at = Column(DateTime(timezone=True), nullable=True)
    customer_reference = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True) # avoiding SQLAlchemy metadata collision
    
    refunds = relationship("Refund", back_populates="payment")

class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(String, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, index=True)
    fees = Column(Integer, default=0)
    tax = Column(Integer, default=0)
    utr = Column(String, index=True, nullable=True)
    settled_at = Column(DateTime(timezone=True), nullable=True)
    payment_references = Column(JSON, nullable=True) # e.g. list of payment IDs or descriptions

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(String, primary_key=True, index=True)
    payment_id = Column(String, ForeignKey("payments.id"), index=True)
    amount = Column(Integer, nullable=False)
    status = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    payment = relationship("Payment", back_populates="refunds")

class BankRecord(Base):
    __tablename__ = "bank_records"

    id = Column(String, primary_key=True, index=True)
    reference = Column(String, index=True, nullable=True)
    amount = Column(Integer, nullable=False)
    transaction_date = Column(DateTime(timezone=True))
    description = Column(String)
    utr = Column(String, index=True, nullable=True)

class ReconciliationResult(Base):
    __tablename__ = "reconciliation_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_record_id = Column(String, index=True)
    candidate_record_id = Column(String, index=True)
    match_type = Column(String) # e.g., EXACT_MATCH, CANDIDATE_MATCH
    match_score = Column(Float)
    status = Column(String) # e.g., RESOLVED, EXCEPTION
    reason = Column(String, nullable=True)

class InvestigationCase(Base):
    __tablename__ = "investigation_cases"

    id = Column(String, primary_key=True, index=True)
    case_type = Column(String, index=True)
    severity = Column(String)
    status = Column(String, index=True)
    evidence = Column(JSON) # Evidence Graph representation
    candidate_matches = Column(JSON, nullable=True)
    ai_analysis = Column(JSON, nullable=True) # Structured output from AI
    confidence = Column(Float, nullable=True)
    decision = Column(String, nullable=True)

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    entity_type = Column(String, index=True)
    entity_id = Column(String, index=True)
    action = Column(String)
    actor = Column(String) # SYSTEM, USER, AI
    reason = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    policy_version = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
