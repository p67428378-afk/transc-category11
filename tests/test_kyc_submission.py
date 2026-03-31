
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date
import pytest

from app.models.kyc_model import CustomerKYC

def test_submit_kyc_success(client: TestClient, session: Session):
    kyc_data = {
        "customer_id": "CUST001",
        "name": "John Doe",
        "date_of_birth": "1990-01-01",
        "aadhaar_number": "123456789012",
        "pan_number": "ABCDE1234F"
    }
    response = client.post("/api/v1/kyc/submit", json=kyc_data)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == "CUST001"
    assert data["name"] == "John Doe"
    assert data["date_of_birth"] == "1990-01-01"
    assert data["aadhaar_number"] == "123456789012"
    assert data["pan_number"] == "ABCDE1234F"
    assert "kyc_id" in data
    assert "submission_timestamp" in data
    assert data["status"] == "VALIDATED"

    # Verify it's in the database
    db_kyc = session.query(CustomerKYC).filter(CustomerKYC.customer_id == "CUST001").first()
    assert db_kyc is not None
    assert db_kyc.name == "John Doe"

def test_submit_kyc_duplicate_customer_id(client: TestClient, session: Session):
    kyc_data = {
        "customer_id": "CUST002",
        "name": "Jane Doe",
        "date_of_birth": "1985-05-10",
        "aadhaar_number": "987654321098",
        "pan_number": "FGHIJ5678K"
    }
    client.post("/api/v1/kyc/submit", json=kyc_data)

    response = client.post("/api/v1/kyc/submit", json=kyc_data)
    assert response.status_code == 409
    assert response.json() == {"detail": "KYC record already exists for this customer_id"}

def test_submit_kyc_invalid_aadhaar_format(client: TestClient):
    kyc_data = {
        "customer_id": "CUST003",
        "name": "Alice",
        "date_of_birth": "1992-03-15",
        "aadhaar_number": "123", # Invalid length
        "pan_number": "LMNOP1234Q"
    }
    response = client.post("/api/v1/kyc/submit", json=kyc_data)
    assert response.status_code == 422
    assert "aadhaar_number" in response.json()["detail"][0]["loc"]

def test_submit_kyc_invalid_pan_format(client: TestClient):
    kyc_data = {
        "customer_id": "CUST004",
        "name": "Bob",
        "date_of_birth": "1988-11-20",
        "aadhaar_number": "112233445566",
        "pan_number": "1234567890" # Invalid format
    }
    response = client.post("/api/v1/kyc/submit", json=kyc_data)
    assert response.status_code == 422
    assert "pan_number" in response.json()["detail"][0]["loc"]

def test_submit_kyc_future_date_of_birth(client: TestClient):
    future_date = date(date.today().year + 1, 1, 1).isoformat()
    kyc_data = {
        "customer_id": "CUST005",
        "name": "Charlie",
        "date_of_birth": future_date,
        "aadhaar_number": "998877665544",
        "pan_number": "RSTUV9876W"
    }
    response = client.post("/api/v1/kyc/submit", json=kyc_data)
    assert response.status_code == 422
    assert "date_of_birth" in response.json()["detail"][0]["loc"]
    assert "Date of Birth cannot be in the future" in response.json()["detail"][0]["msg"]

def test_get_kyc_details_success(client: TestClient, session: Session):
    kyc_data = {
        "customer_id": "CUST006",
        "name": "David",
        "date_of_birth": "1975-02-28",
        "aadhaar_number": "102938475600",
        "pan_number": "WXYZA1234B"
    }
    post_response = client.post("/api/v1/kyc/submit", json=kyc_data)
    assert post_response.status_code == 201
    kyc_id = post_response.json()["kyc_id"]

    get_response = client.get(f"/api/v1/kyc/{kyc_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["kyc_id"] == kyc_id
    assert data["customer_id"] == "CUST006"

def test_get_kyc_details_not_found(client: TestClient):
    response = client.get("/api/v1/kyc/non_existent_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "KYC record not found"}
