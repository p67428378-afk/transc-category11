from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import LoanApplication, Kyc, Document, AuditTrail
import uuid
import datetime

def test_create_loan_application_success(client: TestClient, session: Session):
    application_data = {
        "applicant_id": str(uuid.uuid4()),
        "loan_type": "Personal Loan",
        "amount_requested": 10000.0,
        "status": "Pending",
        "kyc": {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "address": "123 Main St",
            "ssn": "123-45-678",
            "identification_document_id": str(uuid.uuid4())
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
            "identification_document_id": str(uuid.uuid4())
        }
    }
    response = client.post("/api/v1/loans/application", json=application_data)
    assert response.status_code == 422  # Unprocessable Entity for validation errors

def test_create_loan_application_invalid_data_type(client: TestClient):
    application_data = {
        "applicant_id": str(uuid.uuid4()),
        "loan_type": "Personal Loan",
        "amount_requested": "not_a_number",  # Invalid data type
        "status": "Pending",
        "kyc": {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "address": "123 Main St",
            "ssn": "123-45-678",
            "identification_document_id": str(uuid.uuid4())
        }
    }
    response = client.post("/api/v1/loans/application", json=application_data)
    assert response.status_code == 422  # Unprocessable Entity for validation errors

def test_get_loan_application_status_success(client: TestClient, session: Session):
    # First, create a loan application
    applicant_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    kyc_data = Kyc(
        applicant_id=applicant_id,
        first_name="Jane", last_name="Doe", date_of_birth="1990-01-01",
        address="456 Oak Ave", ssn="987-65-432", identification_document_id=doc_id
    )
    session.add(kyc_data)
    session.commit()
    session.refresh(kyc_data)

    loan_app_data = LoanApplication(
        applicant_id=applicant_id, loan_type="Home Loan", amount_requested=200000.0,
        status="Approved", submission_date=datetime.datetime.utcnow()
    )
    session.add(loan_app_data)
    session.commit()
    session.refresh(loan_app_data)

    response = client.get(f"/api/v1/loans/{loan_app_data.application_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] == loan_app_data.application_id
    assert data["status"] == "Approved"
    assert data["loan_type"] == "Home Loan"

def test_get_loan_application_status_not_found(client: TestClient):
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/loans/{non_existent_id}/status")
    assert response.status_code == 404

def test_risk_assessment_success(client: TestClient, session: Session):
    # Create a loan application first
    applicant_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    kyc_data = Kyc(
        applicant_id=applicant_id,
        first_name="Risk", last_name="User", date_of_birth="1985-05-05",
        address="789 Pine St", ssn="111-22-333", identification_document_id=doc_id
    )
    session.add(kyc_data)
    session.commit()
    session.refresh(kyc_data)

    loan_app_data = LoanApplication(
        applicant_id=applicant_id, loan_type="Car Loan", amount_requested=30000.0,
        status="Pending", submission_date=datetime.datetime.utcnow()
    )
    session.add(loan_app_data)
    session.commit()
    session.refresh(loan_app_data)

    assessment_data = {"application_id": loan_app_data.application_id}
    response = client.post("/api/v1/risk/assessment", json=assessment_data)
    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] == loan_app_data.application_id
    assert "risk_score" in data
    assert "compliance_status" in data
    assert data["status"] != "Pending" # Status should be updated

    # Verify update in DB
    updated_loan_app = session.query(LoanApplication).filter(LoanApplication.application_id == loan_app_data.application_id).first()
    assert updated_loan_app.risk_score is not None
    assert updated_loan_app.compliance_status is not None
    assert updated_loan_app.status != "Pending"

def test_risk_assessment_not_found(client: TestClient):
    non_existent_id = str(uuid.uuid4())
    assessment_data = {"application_id": non_existent_id}
    response = client.post("/api/v1/risk/assessment", json=assessment_data)
    assert response.status_code == 404

def test_document_generation_success(client: TestClient, session: Session):
    # Create a loan application first
    applicant_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    kyc_data = Kyc(
        applicant_id=applicant_id,
        first_name="Doc", last_name="Gen", date_of_birth="1995-11-11",
        address="101 Elm St", ssn="444-55-666", identification_document_id=doc_id
    )
    session.add(kyc_data)
    session.commit()
    session.refresh(kyc_data)

    loan_app_data = LoanApplication(
        applicant_id=applicant_id, loan_type="Education Loan", amount_requested=50000.0,
        status="Approved", submission_date=datetime.datetime.utcnow()
    )
    session.add(loan_app_data)
    session.commit()
    session.refresh(loan_app_data)

    document_data = {
        "application_id": loan_app_data.application_id,
        "document_type": "Approval Letter",
        "template_id": "template_001"
    }
    response = client.post("/api/v1/documents/generate", json=document_data)
    assert response.status_code == 200
    data = response.json()
    assert data["loan_application_id"] == loan_app_data.application_id
    assert data["type"] == "Approval Letter"
    assert "document_id" in data
    assert "storage_path" in data

    # Verify document in DB
    generated_doc = session.query(Document).filter(Document.document_id == data["document_id"]).first()
    assert generated_doc is not None
    assert generated_doc.type == "Approval Letter"

def test_document_generation_not_found(client: TestClient):
    non_existent_id = str(uuid.uuid4())
    document_data = {
        "application_id": non_existent_id,
        "document_type": "Approval Letter",
        "template_id": "template_001"
    }
    response = client.post("/api/v1/documents/generate", json=document_data)
    assert response.status_code == 404
