
import uuid
from sqlalchemy import Column, String, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base

class CustomerKYC(Base):
    __tablename__ = "customer_kyc"

    kyc_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    aadhaar_number = Column(String, unique=True, nullable=False)
    pan_number = Column(String, unique=True, nullable=False)
    submission_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="PENDING") # e.g., PENDING, VALIDATED, REJECTED
    validation_errors = Column(String, nullable=True) # Stores JSON string of errors
