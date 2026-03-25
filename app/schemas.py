from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class DocumentBase(BaseModel):
    type: str
    storage_path: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    document_id: str
    loan_application_id: Optional[str] = None
    upload_date: datetime.datetime

    class Config:
        from_attributes = True

class KycBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    address: str
    ssn: str
    identification_document_id: Optional[str] = None

class KycCreate(KycBase):
    pass

class Kyc(KycBase):
    applicant_id: str

    class Config:
        from_attributes = True

class AuditTrailBase(BaseModel):
    action: str
    user_id: str
    details: Optional[str] = None

class AuditTrailCreate(AuditTrailBase):
    pass

class AuditTrail(AuditTrailBase):
    audit_id: str
    loan_application_id: Optional[str] = None
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

class LoanApplicationBase(BaseModel):
    applicant_id: str
    loan_type: str
    amount_requested: float
    status: str = "Pending"
    risk_score: Optional[float] = None
    compliance_status: Optional[str] = None
    loan_officer_id: Optional[str] = None
    comments: Optional[str] = None

class LoanApplicationCreate(LoanApplicationBase):
    kyc: KycCreate

class LoanApplication(LoanApplicationBase):
    application_id: str
    submission_date: datetime.datetime
    decision_date: Optional[datetime.datetime] = None
    kyc: Optional[Kyc] = None
    documents: List[Document] = []
    audit_trails: List[AuditTrail] = []

    class Config:
        from_attributes = True

class RiskAssessmentRequest(BaseModel):
    application_id: str

class RiskAssessmentResponse(BaseModel):
    application_id: str
    risk_score: float
    compliance_status: str
    status: str

class DocumentGenerationRequest(BaseModel):
    application_id: str
    document_type: str
    template_id: str

class DocumentGenerationResponse(BaseModel):
    loan_application_id: str
    document_id: str
    type: str
    storage_path: str
