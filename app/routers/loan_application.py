from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import uuid
import datetime

from app.database import get_db
from app.models import LoanApplication, Kyc, Document, AuditTrail
from app.schemas import LoanApplicationCreate, LoanApplication as LoanApplicationSchema, KycCreate, DocumentCreate, AuditTrailCreate, Document as DocumentSchema, AuditTrail as AuditTrailSchema

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
        application_id=str(uuid.uuid4()), # Generate application_id here
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
        audit_id=str(uuid.uuid4()), # Generate audit_id here
        loan_application_id=db_loan_application.application_id,
        action="Application Submitted",
        user_id=application.applicant_id, # Assuming applicant_id as user_id for submission
        timestamp=datetime.datetime.utcnow(),
        details=f"Loan application {db_loan_application.application_id} submitted by {application.applicant_id}"
    )
    db.add(db_audit_trail)
    db.commit()
    db.refresh(db_audit_trail)

    # Eagerly load relationships for the response model
    db_loan_application = db.query(LoanApplication).options(joinedload(LoanApplication.kyc)).filter(LoanApplication.application_id == db_loan_application.application_id).first()

    return db_loan_application

@router.get("/api/v1/loans/{application_id}/status", response_model=LoanApplicationSchema, status_code=status.HTTP_200_OK)
def get_loan_application_status(
    application_id: str,
    db: Session = Depends(get_db)
):
    loan_application = db.query(LoanApplication).options(joinedload(LoanApplication.kyc)).filter(LoanApplication.application_id == application_id).first()
    if not loan_application:
        raise HTTPException(status_code=404, detail="Loan application not found")
    return loan_application

@router.post("/api/v1/risk/assessment", status_code=status.HTTP_200_OK)
def trigger_risk_assessment(
    payload: dict, # Expecting {"application_id": "..."}
    db: Session = Depends(get_db)
):
    application_id = payload.get("application_id")
    if not application_id:
        raise HTTPException(status_code=400, detail="application_id is required")

    loan_application = db.query(LoanApplication).filter(LoanApplication.application_id == application_id).first()
    if not loan_application:
        raise HTTPException(status_code=404, detail="Loan application not found")

    # Simulate risk assessment
    loan_application.status = "Risk Assessed"
    loan_application.risk_score = 0.25 # Dummy risk score
    loan_application.decision_date = datetime.datetime.utcnow()
    db.add(loan_application)
    db.commit()
    db.refresh(loan_application)

    # Add audit trail
    db_audit_trail = AuditTrail(
        audit_id=str(uuid.uuid4()),
        loan_application_id=loan_application.application_id,
        action="Risk Assessment Triggered",
        user_id="system", # Assuming system user for automated assessment
        timestamp=datetime.datetime.utcnow(),
        details=f"Risk assessment completed for application {loan_application.application_id}. Score: {loan_application.risk_score}"
    )
    db.add(db_audit_trail)
    db.commit()
    db.refresh(db_audit_trail)

    return {"message": "Risk assessment triggered successfully", "application_id": loan_application.application_id}

@router.post("/api/v1/documents/generate", status_code=status.HTTP_200_OK)
def generate_document(
    payload: dict, # Expecting {"application_id": "...", "document_type": "..."}
    db: Session = Depends(get_db)
):
    application_id = payload.get("application_id")
    document_type = payload.get("document_type")
    if not application_id or not document_type:
        raise HTTPException(status_code=400, detail="application_id and document_type are required")

    loan_application = db.query(LoanApplication).filter(LoanApplication.application_id == application_id).first()
    if not loan_application:
        raise HTTPException(status_code=404, detail="Loan application not found")

    # Simulate document generation and storage
    storage_path = f"/documents/{application_id}/{document_type}_{str(uuid.uuid4())}.pdf"
    db_document = Document(
        document_id=str(uuid.uuid4()),
        loan_application_id=application_id,
        type=document_type,
        storage_path=storage_path,
        upload_date=datetime.datetime.utcnow()
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Add audit trail
    db_audit_trail = AuditTrail(
        audit_id=str(uuid.uuid4()),
        loan_application_id=loan_application.application_id,
        action="Document Generated",
        user_id="system", # Assuming system user
        timestamp=datetime.datetime.utcnow(),
        details=f"Document '{document_type}' generated for application {loan_application.application_id}. Path: {storage_path}"
    )
    db.add(db_audit_trail)
    db.commit()
    db.refresh(db_audit_trail)

    return {"message": "Document generation triggered successfully", "document_id": db_document.document_id}
