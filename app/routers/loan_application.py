from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
import datetime

from app.database import get_db
from app.models import LoanApplication, Kyc, Document, AuditTrail
from app.schemas import (
    LoanApplicationCreate, LoanApplication as LoanApplicationSchema, KycCreate, DocumentCreate, AuditTrailCreate,
    RiskAssessmentRequest, RiskAssessmentResponse, DocumentGenerationRequest, DocumentGenerationResponse
)

router = APIRouter()

@router.post("/api/v1/loans/application", response_model=LoanApplicationSchema, status_code=status.HTTP_200_OK)
def create_loan_application(
    application: LoanApplicationCreate,
    db: Session = Depends(get_db)
):
    # Check if KYC entry already exists for the given applicant_id
    db_kyc = db.query(Kyc).filter(Kyc.applicant_id == application.applicant_id).first()
    if not db_kyc:
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
    else:
        # Update existing KYC entry if needed (not explicitly in AC, but good practice)
        db_kyc.first_name = application.kyc.first_name
        db_kyc.last_name = application.kyc.last_name
        db_kyc.date_of_birth = application.kyc.date_of_birth
        db_kyc.address = application.kyc.address
        db_kyc.ssn = application.kyc.ssn
        db_kyc.identification_document_id = application.kyc.identification_document_id
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
    # Eagerly load relationships for the response
    db_loan_application.kyc = db_kyc

    return db_loan_application

@router.get("/api/v1/loans/{application_id}/status", response_model=LoanApplicationSchema)
def get_loan_application_status(
    application_id: str,
    db: Session = Depends(get_db)
):
    loan_application = db.query(LoanApplication).filter(LoanApplication.application_id == application_id).first()
    if not loan_application:
        raise HTTPException(status_code=404, detail="Loan Application not found")
    return loan_application

@router.post("/api/v1/risk/assessment", response_model=RiskAssessmentResponse)
def assess_risk(
    request: RiskAssessmentRequest,
    db: Session = Depends(get_db)
):
    loan_application = db.query(LoanApplication).filter(LoanApplication.application_id == request.application_id).first()
    if not loan_application:
        raise HTTPException(status_code=404, detail="Loan Application not found")

    # Simulate risk assessment and compliance check
    risk_score = 0.75 # Example score
    compliance_status = "Passed" # Example status
    new_status = "Under Review" # Example new status

    loan_application.risk_score = risk_score
    loan_application.compliance_status = compliance_status
    loan_application.status = new_status
    db.commit()
    db.refresh(loan_application)

    # Add audit trail for risk assessment
    db_audit_trail = AuditTrail(
        loan_application_id=loan_application.application_id,
        action="Risk Assessment Performed",
        user_id="system", # Assuming system user for automated assessment
        details=f"Risk score: {risk_score}, Compliance status: {compliance_status}"
    )
    db.add(db_audit_trail)
    db.commit()
    db.refresh(db_audit_trail)

    return RiskAssessmentResponse(
        application_id=loan_application.application_id,
        risk_score=loan_application.risk_score,
        compliance_status=loan_application.compliance_status,
        status=loan_application.status
    )

@router.post("/api/v1/documents/generate", response_model=DocumentGenerationResponse)
def generate_document(
    request: DocumentGenerationRequest,
    db: Session = Depends(get_db)
):
    loan_application = db.query(LoanApplication).filter(LoanApplication.application_id == request.application_id).first()
    if not loan_application:
        raise HTTPException(status_code=404, detail="Loan Application not found")

    # Simulate document generation and storage
    document_id = str(uuid.uuid4())
    storage_path = f"s3://loan-documents/{loan_application.application_id}/{document_id}.pdf"

    db_document = Document(
        document_id=document_id,
        loan_application_id=loan_application.application_id,
        type=request.document_type,
        storage_path=storage_path
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Add audit trail for document generation
    db_audit_trail = AuditTrail(
        loan_application_id=loan_application.application_id,
        action=f"Document Generated: {request.document_type}",
        user_id="system", # Assuming system user for automated generation
        details=f"Document ID: {document_id}, Path: {storage_path}"
    )
    db.add(db_audit_trail)
    db.commit()
    db.refresh(db_audit_trail)

    return DocumentGenerationResponse(
        loan_application_id=loan_application.application_id,
        document_id=db_document.document_id,
        type=db_document.type,
        storage_path=db_document.storage_path
    )
