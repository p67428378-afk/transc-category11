from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import LoanApplication, Kyc

def test_create_loan_application_success(client: TestClient, session: Session):
    application_data = {
        "applicant_id": "test_applicant_123",
        "loan_type": "Personal Loan",
        "amount_requested": 10000.0,
        "status": "Pending",
        "kyc": {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "address": "123 Main St",
            "ssn": "123-45-678",
            "identification_document_id": "doc_id_1"
        }
    }
    response = client.post("/api/v1/loans/application", json=application_data)
    assert response.status_code == 200
    data = response.json()
    assert data["loan_type"] == "Personal Loan"
    assert data["kyc"]["first_name"] == "John"
    assert "application_id" in data

    # Verify data in the database
    loan_app = session.query(LoanApplication).filter(LoanApplication.application_id == data["application_id"]).first()
    assert loan_app is not None
    assert loan_app.loan_type == "Personal Loan"
    assert loan_app.kyc.first_name == "John"

def test_create_loan_application_missing_fields(client: TestClient):
    application_data = {
        "loan_type": "Personal Loan",
        "amount_requested": 10000.0,
        "kyc": {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "address": "123 Main St",
            "ssn": "123-45-678",
            "identification_document_id": "doc_id_1"
        }
    }
    response = client.post("/api/v1/loans/application", json=application_data)
    assert response.status_code == 422  # Unprocessable Entity for validation errors

def test_create_loan_application_invalid_data_type(client: TestClient):
    application_data = {
        "applicant_id": "test_applicant_123",
        "loan_type": "Personal Loan",
        "amount_requested": "not_a_number",  # Invalid data type
        "status": "Pending",
        "kyc": {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "address": "123 Main St",
            "ssn": "123-45-678",
            "identification_document_id": "doc_id_1"
        }
    }
    response = client.post("/api/v1/loans/application", json=application_data)
    assert response.status_code == 422  # Unprocessable Entity for validation errors
