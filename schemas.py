from datetime import date
from typing import Optional
from pydantic import BaseModel

class PremiumCalculationRequest(BaseModel):
    vehicleType: str
    ncbYears: int

class PremiumCalculationResponse(BaseModel):
    annualPremium: float

class PolicyHolderBase(BaseModel):
    name: str
    dateOfBirth: date
    address: str
    contactInfo: str
    ncbYears: int

class PolicyHolderCreate(PolicyHolderBase):
    pass

class PolicyHolder(PolicyHolderBase):
    policyHolderId: str

    class Config:
        from_attributes = True

class VehicleBase(BaseModel):
    make: str
    model: str
    year: int
    vehicleType: str
    vehicleMultiplier: float

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    vehicleId: str
    policyId: str

    class Config:
        from_attributes = True

class PolicyBase(BaseModel):
    policyHolderId: str
    startDate: date
    endDate: date
    basePremium: float
    calculatedPremium: float
    ncbDiscountApplied: float
    status: str

class PolicyCreate(PolicyBase):
    vehicle: VehicleCreate

class Policy(PolicyBase):
    policyId: str
    vehicle: Vehicle

    class Config:
        from_attributes = True

class NCBTierBase(BaseModel):
    ncbYears: int
    discountPercentage: float

class NCBTierCreate(NCBTierBase):
    pass

class NCBTier(NCBTierBase):
    class Config:
        from_attributes = True
