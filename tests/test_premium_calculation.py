import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date

from main import app
from models import PolicyHolder, Vehicle, Policy, NCBTier
from schemas import PremiumCalculationRequest, PremiumCalculationResponse
from services.premium_service import PremiumService

# Test cases for PremiumService.calculate_premium
@pytest.mark.parametrize(
    "vehicle_type, ncb_years, expected_premium",
    [
        # Base case: Sedan, 0 NCB years (0% discount)
        ("Sedan", 0, 500.00),
        # Example from Jira: Sedan, 3 NCB years (30% discount)
        ("Sedan", 3, 350.00), # (500 * 1.0) * (1 - 0.30) = 350
        # Minimum Multiplier: Motorcycle, 1 NCB year (20% discount)
        ("Motorcycle", 1, 320.00), # (500 * 0.8) * (1 - 0.20) = 400 * 0.8 = 320
        # Maximum Multiplier: Sports Car, 2 NCB years (25% discount)
        ("Sports Car", 2, 600.00), # (500 * 1.6) * (1 - 0.25) = 800 * 0.75 = 600
        # Maximum NCB Discount: SUV, 5+ NCB years (50% discount)
        ("SUV", 5, 300.00), # (500 * 1.2) * (1 - 0.50) = 600 * 0.5 = 300
        ("SUV", 10, 300.00), # (500 * 1.2) * (1 - 0.50) = 600 * 0.5 = 300 (capped)
        # Unknown vehicle type, 0 NCB years (default multiplier 1.0)
        ("Van", 0, 500.00), # (500 * 1.0) * (1 - 0.0) = 500
        # Unknown vehicle type, 3 NCB years (default multiplier 1.0, 30% discount)
        ("Van", 3, 350.00), # (500 * 1.0) * (1 - 0.30) = 350
        # Edge case: negative ncb_years should be treated as 0
        ("Sedan", -1, 500.00), # (500 * 1.0) * (1 - 0.0) = 500
    ],
)
def test_calculate_premium_logic(vehicle_type: str, ncb_years: int, expected_premium: float):
    service = PremiumService()
    calculated_premium = service.calculate_premium(vehicle_type, ncb_years)
    assert calculated_premium == expected_premium

# Test cases for the API endpoint
def test_calculate_premium_api_success(client: TestClient):
    response = client.post(
        "/api/v1/premiums/calculate",
        json={
            "vehicleType": "Sedan",
            "ncbYears": 3
        }
    )
    assert response.status_code == 200
    assert response.json() == {"annualPremium": 350.00}

def test_calculate_premium_api_invalid_vehicle_type(client: TestClient):
    response = client.post(
        "/api/v1/premiums/calculate",
        json={
            "vehicleType": 123, # Invalid type
            "ncbYears": 3
        }
    )
    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation error

def test_calculate_premium_api_invalid_ncb_years(client: TestClient):
    response = client.post(
        "/api/v1/premiums/calculate",
        json={
            "vehicleType": "Sedan",
            "ncbYears": "three" # Invalid type
        }
    )
    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation error

def test_create_policy_not_implemented(client: TestClient):
    response = client.post(
        "/api/v1/policies",
        json={
            "policyHolderId": "some_id",
            "startDate": "2023-01-01",
            "endDate": "2024-01-01",
            "basePremium": 500.0,
            "calculatedPremium": 420.0,
            "ncbDiscountApplied": 0.3,
            "status": "Active",
            "vehicle": {
                "make": "Toyota",
                "model": "Camry",
                "year": 2020,
                "vehicleType": "Sedan",
                "vehicleMultiplier": 1.0
            }
        }
    )
    assert response.status_code == 501
    assert response.json() == {"detail": "Policy creation not yet implemented"}

# Test for database models (using session fixture)
def test_create_policy_holder(session: Session):
    policy_holder = PolicyHolder(
        name="John Doe",
        dateOfBirth=date(1990, 5, 15),
        address="123 Main St",
        contactInfo="john.doe@example.com",
        ncbYears=3
    )
    session.add(policy_holder)
    session.commit()
    session.refresh(policy_holder)

    assert policy_holder.policyHolderId is not None
    assert policy_holder.name == "John Doe"

def test_create_ncb_tier(session: Session):
    ncb_tier = NCBTier(ncbYears=6, discountPercentage=0.55)
    session.add(ncb_tier)
    session.commit()
    session.refresh(ncb_tier)

    assert ncb_tier.ncbYears == 6
    assert ncb_tier.discountPercentage == 0.55

def test_create_policy_with_vehicle(session: Session):
    policy_holder = PolicyHolder(
        name="Jane Doe",
        dateOfBirth=date(1985, 10, 20),
        address="456 Oak Ave",
        contactInfo="jane.doe@example.com",
        ncbYears=5
    )
    session.add(policy_holder)
    session.commit()
    session.refresh(policy_holder)

    policy = Policy(
        policyHolderId=policy_holder.policyHolderId,
        startDate=date(2023, 1, 1),
        endDate=date(2024, 1, 1),
        basePremium=500.0,
        calculatedPremium=250.0,
        ncbDiscountApplied=0.5,
        status="Active"
    )
    session.add(policy)
    session.commit()
    session.refresh(policy)

    vehicle = Vehicle(
        policyId=policy.policyId,
        make="Honda",
        model="CRV",
        year=2022,
        vehicleType="SUV",
        vehicleMultiplier=1.2
    )
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)

    assert policy.policyId is not None
    assert policy.policyHolder.name == "Jane Doe"
    assert policy.vehicle.make == "Honda"
