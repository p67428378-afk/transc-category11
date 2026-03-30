from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class PremiumCalculationRequest(BaseModel):
    vehicle_type: str = Field(..., example="Sedan")
    ncb_years: int = Field(..., ge=0, example=3)

class PremiumCalculationResponse(BaseModel):
    annual_premium: float = Field(..., example=300.00)

class PolicyBase(BaseModel):
    vehicle_type: str
    ncb_years: int
    start_date: date
    end_date: date

class PolicyCreate(PolicyBase):
    pass

class Policy(PolicyBase):
    policy_id: str
    base_premium: float
    ncb_discount_percentage: float
    vehicle_multiplier: float
    final_premium: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
