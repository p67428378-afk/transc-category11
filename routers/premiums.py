from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import PremiumCalculationRequest, PremiumCalculationResponse, PolicyCreate, Policy
from services.premium_calculator import calculate_premium
from database import get_db
from models import Policy as DBPolicy
from datetime import date

router = APIRouter(
    prefix="/api/v1/premiums",
    tags=["premiums"]
)

@router.post("/calculate", response_model=PremiumCalculationResponse)
def calculate_insurance_premium(
    request: PremiumCalculationRequest,
    db: Session = Depends(get_db)
):
    try:
        final_premium = calculate_premium(request.vehicle_type, request.ncb_years)

        # For now, we'll just return the premium. Policy persistence will be added later if needed.
        # The HLD mentions persisting policy data, but the AC for the API endpoint only asks for the premium.
        # Let's create a dummy policy record for now to satisfy the HLD's data model requirement.
        # In a real scenario, this would be a separate endpoint or part of a policy creation flow.
        dummy_policy = DBPolicy(
            vehicle_type=request.vehicle_type,
            ncb_years=request.ncb_years,
            base_premium=500.00, # Hardcoded as per AC
            ncb_discount_percentage=0.0, # Placeholder
            vehicle_multiplier=0.0, # Placeholder
            final_premium=final_premium,
            start_date=date.today(),
            end_date=date.today(),
        )
        # db.add(dummy_policy)
        # db.commit()
        # db.refresh(dummy_policy)

        return PremiumCalculationResponse(annual_premium=final_premium)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
