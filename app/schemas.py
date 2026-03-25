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

class CreditCheckBase(BaseModel):
    applicant_id: str
    loan_application_id: Optional[str] = None
    credit_score: float
    credit_report_id: Optional[str] = None
    report_date: Optional[datetime.datetime] = None
    bureau_source: str

class CreditCheckCreate(CreditCheckBase):
    pass

class CreditCheck(CreditCheckBase):
    credit_check_id: str

    class Config:
        from_attributes = True

class EmploymentBase(BaseModel):
    applicant_id: str
    loan_application_id: Optional[str] = None
    employer_name: str
    job_title: str
    annual_income: float
    income_verification_document_id: Optional[str] = None

class EmploymentCreate(EmploymentBase):
    pass

class Employment(EmploymentBase):
    employment_id: str

    class Config:
        from_attributes = True

class CollateralBase(BaseModel):
    loan_application_id: str
    type: str
    value: float
    document_id: Optional[str] = None

class CollateralCreate(CollateralBase):
    pass

class Collateral(CollateralBase):
    collateral_id: str

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
    credit_checks: Optional[List[CreditCheckCreate]] = None
    employments: Optional[List[EmploymentCreate]] = None
    collaterals: Optional[List[CollateralCreate]] = None

class LoanApplication(LoanApplicationBase):
    application_id: str
    submission_date: datetime.datetime
    decision_date: Optional[datetime.datetime] = None
    kyc: Optional[Kyc] = None
    documents: List[Document] = []
    audit_trails: List[AuditTrail] = []
    credit_checks: List[CreditCheck] = []
    employments: List[Employment] = []
    collaterals: List[Collateral] = []

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
