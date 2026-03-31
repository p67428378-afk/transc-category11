import pytest
from fastapi.testclient import TestClient
from datetime import date
import uuid

# Assuming app.main.app is the FastAPI application instance
# and app.db.session.get_db is the dependency for database sessions.
# These will be mocked or overridden in conftest.py

def test_create_kyc_successful(client: TestClient, db_session):
    customer_uuid = str(uuid.uuid4())
    kyc_data = {
        "name": "John Doe",
        "date_of_birth": "1990-01-01",
        "aadhaar_number": "123456789012",
        "pan_number": "ABCDE1234F",
        "customer_id": customer_uuid
    }
    response = client.post("/api/v1/kyc/submit", json=kyc_data)
    print(response.json()) # Debugging line
    assert response.status_code == 200
    assert response.json()["name"] == kyc_data["name"]
    assert response.json()["aadhaar_number"] == kyc_data["aadhaar_number"]
    assert response.json()["pan_number"] == kyc_data["pan_number"]
    assert response.json()["status"] == "PENDING"
    assert "kyc_id" in response.json()
    assert response.json()["customer_id"] == customer_uuid

def test_create_kyc_invalid_aadhaar_format(client: TestClient):
    kyc_data = {
        "name": "Jane Doe",
        "date_of_birth": "1985-05-10",
        "aadhaar_number": "12345",  # Invalid format
        "pan_number": "FGHIJ5678K",
        "customer_id": str(uuid.uuid4())
    }
    response = client.post("/api/v1/kyc/submit", json=kyc_data)
    assert response.status_code == 422  # Unprocessable Entity for validation errors
    assert "aadhaar_number" in response.text

def test_create_kyc_invalid_pan_format(client: TestClient):
    kyc_data = {
        "name": "Peter Pan",
        "date_of_birth": "1970-11-20",
        "aadhaar_number": "987654321098",
        "pan_number": "INVALID",  # Invalid format
        "customer_id": str(uuid.uuid4())
    }
    response = client.post("/api/v1/kyc/submit", json=kyc_data)
    assert response.status_code == 422
    assert "pan_number" in response.text

def test_create_kyc_missing_field(client: TestClient):
    kyc_data = {
        "date_of_birth": "2000-03-15",
        "aadhaar_number": "112233445566",
        "pan_number": "LMNOP0123Q",
        "customer_id": str(uuid.uuid4())
    }
    response = client.post("/api/v1/kyc/submit", json=kyc_data)
    assert response.status_code == 422
    assert "name" in response.text

def test_create_kyc_future_date_of_birth(client: TestClient):
    future_date = date(date.today().year + 1, 1, 1).isoformat()
    kyc_data = {
        "name": "Future Kid",
        "date_of_birth": future_date,
        "aadhaar_number": "111122223333",
        "pan_number": "QRSTU5678V",
        "customer_id": str(uuid.uuid4())
    }
    response = client.post("/api/v1/kyc/submit", json=kyc_data)
    assert response.status_code == 422
    assert "Date of Birth cannot be in the future" in response.text
