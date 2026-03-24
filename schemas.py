
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LoanApplicationBase(BaseModel):
    applicant_id: str
    loan_amount: float
    credit_score: Optional[int] = None
    income: Optional[float] = None

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

    class Config:
        from_attributes = True
