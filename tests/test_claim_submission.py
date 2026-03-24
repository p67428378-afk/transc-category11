import pytest
from fastapi.testclient import TestClient
from datetime import date

from app.main import app # Import the actual FastAPI app

@pytest.fixture(name="client")
def test_client():
    with TestClient(app) as client:
        yield client

def test_successful_claim_submission(client):
    """
    Scenario 1: Successful Claim Submission
    The user can successfully submit a claim with all required details.
    The system validates the information and returns an approval decision.
    """
    claim_data = {
        "policy_number": "POL-12345",
        "incident_date": "2023-01-15",
        "description": "Car accident, minor damage to front bumper.",
        "user_id": "user-abc",
        "attachments": ["photo1.jpg", "photo2.jpg"]
    }
    response = client.post("/api/claims/submit", json=claim_data)
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert "claim_id" in response.json()
    assert response.json()["reason"] == "Claim processed successfully"

def test_claim_submission_missing_policy_number(client):
    """
    Scenario 2: Claim Submission with Missing/Invalid Details - Missing policy_number
    If the user submits a claim with missing required details, the system should reject the submission
    and provide clear reasons for rejection.
    """
    claim_data = {
        "incident_date": "2023-01-15",
        "description": "Car accident, minor damage to front bumper.",
        "user_id": "user-abc",
        "attachments": ["photo1.jpg"]
    }
    response = client.post("/api/claims/submit", json=claim_data)
    assert response.status_code == 422 # Expecting Pydantic validation error
    assert response.json()["detail"][0]["loc"] == ["body", "policy_number"]
    assert response.json()["detail"][0]["type"] == "missing"

def test_claim_submission_future_incident_date(client):
    """
    Scenario 2: Claim Submission with Missing/Invalid Details - Future incident_date
    Submitting a date of incident in the future should result in rejection.
    """
    future_date = (date.today().replace(year=date.today().year + 1)).isoformat()
    claim_data = {
        "policy_number": "POL-12345",
        "incident_date": future_date,
        "description": "Future incident.",
        "user_id": "user-abc"
    }
    response = client.post("/api/claims/submit", json=claim_data)
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["reason"] == "Incident date cannot be in the future"

def test_claim_submission_invalid_incident_date_format(client):
    """
    Scenario 2: Claim Submission with Missing/Invalid Details - Invalid incident_date format
    Submitting an invalid date format should result in rejection.
    """
    claim_data = {
        "policy_number": "POL-12345",
        "incident_date": "15-01-2023", # Invalid format
        "description": "Invalid date format.",
        "user_id": "user-abc"
    }
    response = client.post("/api/claims/submit", json=claim_data)
    assert response.status_code == 422 # Expecting Pydantic validation error
    assert response.json()["detail"][0]["loc"] == ["body", "incident_date"]
    assert response.json()["detail"][0]["type"] == "date_from_datetime_parsing"

def test_claim_submission_invalid_policy_number(client):
    """
    Scenario 2: Claim Submission with Missing/Invalid Details - Invalid policy number
    Mocking the decision engine to reject based on policy number.
    """
    claim_data = {
        "policy_number": "INVALID-POLICY",
        "incident_date": "2023-03-20",
        "description": "Claim with an invalid policy number.",
        "user_id": "user-abc"
    }
    response = client.post("/api/claims/submit", json=claim_data)
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["reason"] == "Invalid policy number"

def test_claim_submission_potential_fraud(client):
    """
    Scenario 2: Claim Submission with Missing/Invalid Details - Potential fraud
    Mocking the decision engine to reject based on potential fraud.
    """
    claim_data = {
        "policy_number": "FRAUD-POLICY",
        "incident_date": "2023-03-20",
        "description": "Claim with potential fraud.",
        "user_id": "user-abc"
    }
    response = client.post("/api/claims/submit", json=claim_data)
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["reason"] == "Potential fraud detected"

def test_claim_submission_description_too_short(client):
    """
    Scenario 2: Claim Submission with Missing/Invalid Details - Description too short
    """
    claim_data = {
        "policy_number": "POL-12345",
        "incident_date": "2023-01-15",
        "description": "short", # Less than 10 characters
        "user_id": "user-abc",
        "attachments": ["photo1.jpg"]
    }
    response = client.post("/api/claims/submit", json=claim_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "description"]
    assert response.json()["detail"][0]["type"] == "string_too_short"

def test_claim_submission_empty_policy_number(client):
    """
    Scenario 2: Claim Submission with Missing/Invalid Details - Empty policy number
    """
    claim_data = {
        "policy_number": "",
        "incident_date": "2023-01-15",
        "description": "Car accident, minor damage to front bumper.",
        "user_id": "user-abc",
        "attachments": ["photo1.jpg"]
    }
    response = client.post("/api/claims/submit", json=claim_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "policy_number"]
    assert response.json()["detail"][0]["type"] == "string_too_short"

def test_claim_submission_empty_user_id(client):
    """
    Scenario 2: Claim Submission with Missing/Invalid Details - Empty user ID
    """
    claim_data = {
        "policy_number": "POL-12345",
        "incident_date": "2023-01-15",
        "description": "Car accident, minor damage to front bumper.",
        "user_id": "",
        "attachments": ["photo1.jpg"]
    }
    response = client.post("/api/claims/submit", json=claim_data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "user_id"]
    assert response.json()["detail"][0]["type"] == "string_too_short"
