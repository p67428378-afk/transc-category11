from datetime import date, datetime
from typing import Optional, Annotated
from uuid import UUID

from pydantic import BaseModel, Field, BeforeValidator, ConfigDict

# Custom type for UUID string to handle potential conversion from UUID object
PyUUID = Annotated[str, BeforeValidator(lambda x: str(x))]


class KycBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    aadhaar_number: str = Field(..., pattern=r"^\d{12}$")
    pan_number: str = Field(..., pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")


class KycCreate(KycBase):
    customer_id: str


class KycUpdate(KycBase):
    pass


class KycInDBBase(KycBase):
    kyc_id: PyUUID
    customer_id: PyUUID
    submission_timestamp: datetime
    status: str
    validation_errors: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Kyc(KycInDBBase):
    pass
