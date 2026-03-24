from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ValidationError
from datetime import date
from typing import List, Optional

app = FastAPI()

class ClaimSubmissionRequest(BaseModel):
    policy_number: str = Field(..., min_length=1, description="The policy number associated with the claim.")
    incident_date: date = Field(..., description="The date when the incident occurred (YYYY-MM-DD).")
    description: str = Field(..., min_length=10, description="A detailed description of the incident.")
    user_id: str = Field(..., min_length=1, description="The ID of the user submitting the claim.")
    attachments: Optional[List[str]] = Field(default_factory=list, description="List of attachment file paths or references.")

@app.post("/api/claims/submit", status_code=status.HTTP_200_OK)
async def submit_claim(claim_request: ClaimSubmissionRequest):
    """
    Submits an insurance claim with the provided details.
    Validates the claim data and returns an approval or rejection decision.
    """
    # Simulate Validation & Decision Engine logic
    # In a real application, this would involve database lookups, external service calls, etc.

    # Incident date validation (cannot be in the future)
    if claim_request.incident_date > date.today():
        return {"status": "rejected", "reason": "Incident date cannot be in the future"}

    # Simulate invalid policy number
    if claim_request.policy_number == "INVALID-POLICY":
        return {"status": "rejected", "reason": "Invalid policy number"}

    # Simulate fraud detection
    if claim_request.policy_number == "FRAUD-POLICY":
        return {"status": "rejected", "reason": "Potential fraud detected"}

    # Simulate successful claim processing
    # In a real scenario, this would involve saving to DB, triggering notifications, etc.
    claim_id = f"CLAIM-{hash(claim_request.policy_number + str(claim_request.incident_date)) % 100000}"
    return {"status": "approved", "claim_id": claim_id, "reason": "Claim processed successfully"}

