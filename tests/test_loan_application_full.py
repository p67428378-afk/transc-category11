from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import LoanApplication, Kyc, Document, AuditTrail
from app.schemas import LoanApplicationCreate, KycCreate, DocumentCreate, AuditTrailCreate
import datetime
import uuid

def test_create_loan_application_success(client: TestClient, session: Session):
    kyc_data = KycCreate(
        first_name="Jane",
        last_name="Doe",
        date_of_birth="1995-05-10",
        address="456 Oak Ave",
        ssn="987-65-432",
        identification_document_id=str(uuid.uuid4())
    )
    application_data = LoanApplicationCreate(
        applicant_id=str(uuid.uuid4()),
        loan_type="Mortgage",
        amount_requested=250000.0,
        status="Pending",
        kyc=kyc_data
    )
    response = client.post("/api/v1/loans/application", json=application_data.model_dump(mode='json'))
    assert response.status_code == 200
    data = response.json()
    assert data["loan_type"] == "Mortgage"
    assert data["kyc"]["first_name"] == "Jane"
    assert "application_id" in data

    loan_app = session.query(LoanApplication).filter(LoanApplication.application_id == data["application_id"]).first()
    assert loan_app is not None
    assert loan_app.loan_type == "Mortgage"
    assert loan_app.kyc.first_name == "Jane"

def test_create_loan_application_missing_required_fields(client: TestClient):
    # Missing amount_requested
    kyc_data = KycCreate(
        first_name="Jane",
        last_name="Doe",
        date_of_birth="1995-05-10",
        address="456 Oak Ave",
        ssn="987-65-432",
        identification_document_id=str(uuid.uuid4())
    )
    application_data = {
        "applicant_id": str(uuid.uuid4()),
        "loan_type": "Mortgage",
        "status": "Pending",
        "kyc": kyc_data.model_dump(mode='json')
    }
    response = client.post("/api/v1/loans/application", json=application_data)
    assert response.status_code == 422

def test_create_loan_application_invalid_data_type(client: TestClient):
    # Invalid amount_requested type
    kyc_data = KycCreate(
        first_name="Jane",
        last_name="Doe",
        date_of_birth="1995-05-10",
        address="456 Oak Ave",
        ssn="987-65-432",
        identification_document_id=str(uuid.uuid4())
    )
    application_data = {
        "applicant_id": str(uuid.uuid4()),
        "loan_type": "Mortgage",
        "amount_requested": "two hundred thousand",
        "status": "Pending",
        "kyc": kyc_data.model_dump(mode='json')
    }
    response = client.post("/api/v1/loans/application", json=application_data)
    assert response.status_code == 422

def test_get_loan_application_status_success(client: TestClient, session: Session):
    kyc_data = Kyc(
        applicant_id=str(uuid.uuid4()),
        first_name="Test",
        last_name="User",
        date_of_birth="1980-01-01",
        address="789 Pine St",
        ssn="111-22-333",
        identification_document_id=str(uuid.uuid4())
    )
    session.add(kyc_data)
    session.commit()
    session.refresh(kyc_data)

    loan_app = LoanApplication(
        applicant_id=kyc_data.applicant_id,
        loan_type="Auto Loan",
        amount_requested=30000.0,
        status="Approved",
        risk_score=0.1,
        compliance_status="Passed",
        loan_officer_id="LO001",
        comments="Approved based on good credit",
        kyc=kyc_data
    )
    session.add(loan_app)
    session.commit()
    session.refresh(loan_app)

    response = client.get(f"/api/v1/loans/{loan_app.application_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] == loan_app.application_id
    assert data["status"] == "Approved"
    assert data["loan_type"] == "Auto Loan"
    assert data["kyc"]["first_name"] == "Test"

def test_get_loan_application_status_not_found(client: TestClient):
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/loans/{non_existent_id}/status")
    assert response.status_code == 404

def test_risk_assessment_trigger_success(client: TestClient, session: Session):
    kyc_data = Kyc(
        applicant_id=str(uuid.uuid4()),
        first_name="Risk",
        last_name="Applicant",
        date_of_birth="1975-11-20",
        address="101 Elm St",
        ssn="444-55-666",
        identification_document_id=str(uuid.uuid4())
    )
    session.add(kyc_data)
    session.commit()
    session.refresh(kyc_data)

    loan_app = LoanApplication(
        applicant_id=kyc_data.applicant_id,
        loan_type="Business Loan",
        amount_requested=100000.0,
        status="Pending",
        kyc=kyc_data
    )
    session.add(loan_app)
    session.commit()
    session.refresh(loan_app)

    response = client.post(f"/api/v1/risk/assessment", json={"application_id": loan_app.application_id})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Risk assessment triggered successfully"
    assert data["application_id"] == loan_app.application_id

    # Verify status update in DB
    session.refresh(loan_app)
    assert loan_app.status == "Risk Assessed"
    assert loan_app.risk_score is not None

def test_risk_assessment_trigger_not_found(client: TestClient):
    non_existent_id = str(uuid.uuid4())
    response = client.post(f"/api/v1/risk/assessment", json={"application_id": non_existent_id})
    assert response.status_code == 404

def test_document_generation_success(client: TestClient, session: Session):
    kyc_data = Kyc(
        applicant_id=str(uuid.uuid4()),
        first_name="Doc",
        last_name="Gen",
        date_of_birth="1988-03-15",
        address="202 Birch St",
        ssn="777-88-999",
        identification_document_id=str(uuid.uuid4())
    )
    session.add(kyc_data)
    session.commit()
    session.refresh(kyc_data)

    loan_app = LoanApplication(
        applicant_id=kyc_data.applicant_id,
        loan_type="Personal Loan",
        amount_requested=5000.0,
        status="Approved",
        kyc=kyc_data
    )
    session.add(loan_app)
    session.commit()
    session.refresh(loan_app)

    document_request = {
        "application_id": loan_app.application_id,
        "document_type": "Approval Letter"
    }
    response = client.post("/api/v1/documents/generate", json=document_request)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Document generation triggered successfully"
    assert "document_id" in data

    # Verify document creation in DB
    document = session.query(Document).filter(Document.document_id == data["document_id"]).first()
    assert document is not None
    assert document.loan_application_id == loan_app.application_id
    assert document.type == "Approval Letter"
    assert document.storage_path is not None

def test_document_generation_not_found(client: TestClient):
    non_existent_id = str(uuid.uuid4())
    document_request = {
        "application_id": non_existent_id,
        "document_type": "Approval Letter"
    }
    response = client.post("/api/v1/documents/generate", json=document_request)
    assert response.status_code == 404
