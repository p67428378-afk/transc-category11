
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import LoanApplicationCreate, LoanApplicationResponse, LoanApplicationUpdateStatus, AuditLogResponse
from services.loan_application_service import loan_application_service

router = APIRouter()

@router.post("/loan-applications/", response_model=LoanApplicationResponse, status_code=status.HTTP_200_OK)
def create_loan_application(
    application: LoanApplicationCreate,
    db: Session = Depends(get_db)
):
    return loan_application_service.create_loan_application(db, application)

@router.get("/loan-applications/{application_id}", response_model=LoanApplicationResponse, status_code=status.HTTP_200_OK)
def get_loan_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    db_application = loan_application_service.get_loan_application(db, application_id)
    if db_application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    return db_application

@router.put("/loan-applications/{application_id}/status", response_model=LoanApplicationResponse, status_code=status.HTTP_200_OK)
def update_loan_application_status(
    application_id: int,
    update_data: LoanApplicationUpdateStatus,
    db: Session = Depends(get_db)
):
    db_application = loan_application_service.update_loan_application_status(db, application_id, update_data)
    if db_application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")
    return db_application

@router.get("/loan-applications/{application_id}/audit-logs", response_model=List[AuditLogResponse], status_code=status.HTTP_200_OK)
def get_loan_application_audit_logs(
    application_id: int,
    db: Session = Depends(get_db)
):
    # First, check if the loan application exists
    db_application = loan_application_service.get_loan_application(db, application_id)
    if db_application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan application not found")

    return loan_application_service.get_audit_logs_for_application(db, application_id)
