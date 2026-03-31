
from pydantic import BaseModel, Field, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

class AuditLogResponse(BaseModel):
    id: int
    loan_application_id: int
    action: str
    timestamp: datetime
    user_id: Optional[str] = None
    details: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
