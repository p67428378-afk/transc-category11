
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

class LoanHistoryBase(BaseModel):
    previous_loan_amount: float
    outstanding_balance: float
    payment_history: str

class LoanHistoryCreate(LoanHistoryBase):
    pass

class LoanHistoryResponse(LoanHistoryBase):
    id: int
    loan_application_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LoanApplicationBase(BaseModel):
    applicant_id: str
    loan_amount: float
    credit_score: Optional[int] = None
    income: Optional[float] = None
    loan_history: Optional[List[LoanHistoryCreate]] = None

class LoanApplicationCreate(LoanApplicationBase):
    pass

class LoanApplicationUpdateStatus(BaseModel):
    status: str
    decision: Optional[str] = None
    decision_rationale: Optional[str] = None
    approved_by: Optional[str] = None

class LoanApplicationResponse(LoanApplicationBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    risk_assessment: Optional[str] = None
    decision: Optional[str] = None
    decision_rationale: Optional[str] = None
    approved_by: Optional[str] = None
    loan_history: List[LoanHistoryResponse] = []

    model_config = ConfigDict(from_attributes=True)

class AuditLogResponse(BaseModel):
    id: int
    loan_application_id: int
    action: str
    timestamp: datetime
    user_id: Optional[str] = None
    details: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
