from datetime import date
from typing import Optional
import json

from sqlalchemy.orm import Session

from app.models.kyc import CustomerKYC
from app.schemas.kyc import KycCreate


def create_kyc_record(
    db: Session, kyc_data: KycCreate
) -> CustomerKYC:
    # Basic validation for date_of_birth range
    if kyc_data.date_of_birth > date.today():
        raise ValueError("Date of Birth cannot be in the future")

    # In a real application, you might have more complex validation logic here
    # and potentially integrate with external services.

    db_obj = CustomerKYC(
        customer_id=str(kyc_data.customer_id),
        name=kyc_data.name,
        date_of_birth=kyc_data.date_of_birth,
        aadhaar_number=kyc_data.aadhaar_number,
        pan_number=kyc_data.pan_number,
        status="PENDING",  # Initial status
        validation_errors=None, # No errors initially
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
