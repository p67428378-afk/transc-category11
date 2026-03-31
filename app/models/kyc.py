import uuid
from datetime import datetime, UTC

from sqlalchemy import Column, Date, String, DateTime

from app.db.base_class import Base


class CustomerKYC(Base):
    __tablename__ = "customer_kyc"

    kyc_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    aadhaar_number = Column(String, nullable=False)
    pan_number = Column(String, nullable=False)
    submission_timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    status = Column(String, default="PENDING")
    validation_errors = Column(String, nullable=True)
