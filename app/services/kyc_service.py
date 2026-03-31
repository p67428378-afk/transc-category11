
from sqlalchemy.orm import Session
from app.models.kyc_model import CustomerKYC
from app.schemas.kyc_schema import KycCreate
import json

def create_kyc_record(db: Session, kyc_data: KycCreate):
    # In a real application, sensitive data like Aadhaar and PAN would be encrypted
    # before storing. For this exercise, we'll store them as is.
    db_kyc = CustomerKYC(
        customer_id=kyc_data.customer_id,
        name=kyc_data.name,
        date_of_birth=kyc_data.date_of_birth,
        aadhaar_number=kyc_data.aadhaar_number,
        pan_number=kyc_data.pan_number,
        status="VALIDATED" # Assuming validation happens before this service call
    )
    db.add(db_kyc)
    db.commit()
    db.refresh(db_kyc)
    return db_kyc

def get_kyc_record(db: Session, kyc_id: str):
    return db.query(CustomerKYC).filter(CustomerKYC.kyc_id == kyc_id).first()

def get_kyc_by_customer_id(db: Session, customer_id: str):
    return db.query(CustomerKYC).filter(CustomerKYC.customer_id == customer_id).first()
