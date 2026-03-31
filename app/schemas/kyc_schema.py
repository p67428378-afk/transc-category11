
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

class KycBase(BaseModel):
    customer_id: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date
    aadhaar_number: str = Field(..., min_length=12, max_length=12, pattern="^[0-9]{12}$")
    pan_number: str = Field(..., min_length=10, max_length=10, pattern="^[A-Z]{5}[0-9]{4}[A-Z]{1}$")

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v):
        if v >= date.today():
            raise ValueError('Date of Birth cannot be in the future')
        # Add more sophisticated age validation if needed (e.g., min age)
        return v

class KycCreate(KycBase):
    pass

class KycResponse(KycBase):
    kyc_id: str
    submission_timestamp: datetime
    status: str
    validation_errors: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
