from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import LoanApplication, Kyc, Document, AuditTrail
from app.schemas import LoanApplicationCreate, LoanApplication as LoanApplicationSchema, KycCreate, DocumentCreate, AuditTrailCreate

router = APIRouter()

@router.post("/api/v1/loans/application", response_model=LoanApplicationSchema, status_code=status.HTTP_200_OK)
def create_loan_application(
    application: LoanApplicationCreate,
    db: Session = Depends(get_db)
):
    # Create KYC entry
    db_kyc = Kyc(
        applicant_id=application.applicant_id,
        first_name=application.kyc.first_name,
        last_name=application.kyc.last_name,
        date_of_birth=application.kyc.date_of_birth,
        address=application.kyc.address,
        ssn=application.kyc.ssn,
        identification_document_id=application.kyc.identification_document_id
    )
    db.add(db_kyc)
    db.commit()
    db.refresh(db_kyc)

    # Create LoanApplication entry
    db_loan_application = LoanApplication(
        applicant_id=db_kyc.applicant_id,
        loan_type=application.loan_type,
        amount_requested=application.amount_requested,
        status=application.status,
        risk_score=application.risk_score,
        compliance_status=application.compliance_status,
        loan_officer_id=application.loan_officer_id,
        comments=application.comments
    )
    db.add(db_loan_application)
    db.commit()
    db.refresh(db_loan_application)

    # Add a basic audit trail entry for application submission
    db_audit_trail = AuditTrail(
        loan_application_id=db_loan_application.application_id,
        action="Application Submitted",
        user_id=application.applicant_id, # Assuming applicant_id as user_id for submission
        details=f"Loan application {db_loan_application.application_id} submitted by {application.applicant_id}"
    )
    db.add(db_audit_trail)
    db.commit()
    db.refresh(db_audit_trail)

    # Refresh to load relationships for the response model
    db.refresh(db_loan_application)
    db.refresh(db_kyc)

    return db_loan_application
