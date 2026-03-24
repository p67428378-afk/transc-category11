
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
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
