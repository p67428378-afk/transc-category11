
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.kyc_schema import KycCreate, KycResponse
from app.services import kyc_service

router = APIRouter()

@router.post("/kyc/submit", response_model=KycResponse, status_code=status.HTTP_201_CREATED)
def submit_kyc(kyc_data: KycCreate, db: Session = Depends(get_db)):
    # Check if a KYC record already exists for this customer_id
    existing_kyc = kyc_service.get_kyc_by_customer_id(db, kyc_data.customer_id)
    if existing_kyc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="KYC record already exists for this customer_id"
        )

    db_kyc = kyc_service.create_kyc_record(db, kyc_data)
    return db_kyc

@router.get("/kyc/{kyc_id}", response_model=KycResponse)
def get_kyc_details(kyc_id: str, db: Session = Depends(get_db)):
    db_kyc = kyc_service.get_kyc_record(db, kyc_id)
    if db_kyc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KYC record not found")
    return db_kyc
