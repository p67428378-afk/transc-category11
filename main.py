from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine, get_db, Base
import models, schemas
from services.premium_service import PremiumService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Initialize PremiumService
premium_service = PremiumService()

@app.post("/api/v1/premiums/calculate", response_model=schemas.PremiumCalculationResponse)
def calculate_premium_endpoint(
    request: schemas.PremiumCalculationRequest,
    db: Session = Depends(get_db)
):
    try:
        annual_premium = premium_service.calculate_premium(
            vehicle_type=request.vehicleType,
            ncb_years=request.ncbYears
        )
        return {"annualPremium": annual_premium}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Placeholder for policy creation endpoint (as per HLD)
@app.post("/api/v1/policies", response_model=schemas.Policy)
def create_policy_endpoint(
    policy_create: schemas.PolicyCreate,
    db: Session = Depends(get_db)
):
    # This is a placeholder. Actual implementation would involve saving policy details
    # and potentially calculating premium if not already done.
    # For now, we'll just return a dummy policy.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Policy creation not yet implemented")

