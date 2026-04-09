
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(String, index=True, nullable=False)
    loan_amount = Column(Float, nullable=False)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    credit_score = Column(Integer, nullable=True)
    income = Column(Float, nullable=True)
    risk_assessment = Column(String, nullable=True)
    decision = Column(String, nullable=True)
    decision_rationale = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)

    loan_history = relationship("LoanHistory", back_populates="loan_application", cascade="all, delete-orphan")

class LoanHistory(Base):
    __tablename__ = "loan_history"

    id = Column(Integer, primary_key=True, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    previous_loan_amount = Column(Float, nullable=False)
    outstanding_balance = Column(Float, nullable=False)
    payment_history = Column(String, nullable=False) # e.g., "good", "fair", "poor"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    loan_application = relationship("LoanApplication", back_populates="loan_history")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    loan_application_id = Column(Integer, index=True, nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    user_id = Column(String, nullable=True)
    details = Column(String, nullable=True)
