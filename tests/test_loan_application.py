
import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone
import os

# --- Database Setup for Testing ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Models (simplified for testing) ---
class LoanApplication(Base):
    __tablename__ = "loan_applications"
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(String, index=True)
    loan_amount = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Simplified fields based on HLD and Jira
    credit_score = Column(Integer, nullable=True)
    income = Column(Float, nullable=True)
    risk_assessment = Column(String, nullable=True)
    decision = Column(String, nullable=True)
    decision_rationale = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    loan_application_id = Column(Integer, index=True, nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    user_id = Column(String, nullable=True)
    details = Column(String, nullable=True)


# --- Test Fixtures ---
@pytest.fixture(name="db_session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
async def client_fixture(db_session):
    from main import app
    from database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

# --- Tests ---
@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Loan Application API"}

@pytest.mark.asyncio
async def test_create_loan_application(client: AsyncClient):
    response = await client.post(
        "/loan-applications/",
        json={
            "applicant_id": "applicant123",
            "loan_amount": 10000.0,
            "credit_score": 750,
            "income": 60000.0
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["applicant_id"] == "applicant123"
    assert data["loan_amount"] == 10000.0
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["credit_score"] == 750
    assert data["income"] == 60000.0
    assert data["risk_assessment"] == "Low Risk"

    # Verify in database
    db = SessionLocal()
    loan_app = db.query(LoanApplication).filter(LoanApplication.id == data["id"]).first()
    assert loan_app is not None
    assert loan_app.applicant_id == "applicant123"
    assert loan_app.loan_amount == 10000.0
    db.close()

@pytest.mark.asyncio
async def test_create_loan_application_missing_credit_score_income(client: AsyncClient):
    response = await client.post(
        "/loan-applications/",
        json={
            "applicant_id": "applicant_no_score_income",
            "loan_amount": 5000.0
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["applicant_id"] == "applicant_no_score_income"
    assert data["loan_amount"] == 5000.0
    assert data["status"] == "pending"
    assert data["credit_score"] is not None # Should be simulated now
    assert data["income"] is not None # Should be simulated now
    assert data["risk_assessment"] in ["Low Risk", "Medium Risk", "High Risk"] # Can be any due to simulation

@pytest.mark.asyncio
async def test_get_loan_application(client: AsyncClient):
    # First create an application
    create_response = await client.post(
        "/loan-applications/",
        json={
            "applicant_id": "applicant456",
            "loan_amount": 20000.0,
            "credit_score": 680,
            "income": 75000.0
        },
    )
    assert create_response.status_code == 200
    created_data = create_response.json()
    loan_id = created_data["id"]

    # Then retrieve it
    get_response = await client.get(f"/loan-applications/{loan_id}")
    assert get_response.status_code == 200
    retrieved_data = get_response.json()
    assert retrieved_data["id"] == loan_id
    assert retrieved_data["applicant_id"] == "applicant456"
    assert retrieved_data["loan_amount"] == 20000.0
    assert retrieved_data["status"] == "pending"
    assert retrieved_data["credit_score"] == 680
    assert retrieved_data["income"] == 75000.0
    assert retrieved_data["risk_assessment"] == "Low Risk" # Updated logic: 680 credit, 20k/75k = 0.26 < 0.5

@pytest.mark.asyncio
async def test_get_nonexistent_loan_application(client: AsyncClient):
    response = await client.get("/loan-applications/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Loan application not found"}

@pytest.mark.asyncio
async def test_update_loan_application_status(client: AsyncClient):
    # Create an application
    create_response = await client.post(
        "/loan-applications/",
        json={
            "applicant_id": "applicant789",
            "loan_amount": 5000.0,
            "credit_score": 700,
            "income": 50000.0
        },
    )
    assert create_response.status_code == 200
    created_data = create_response.json()
    loan_id = created_data["id"]

    # Update its status to approved
    update_response = await client.put(
        f"/loan-applications/{loan_id}/status",
        json={
            "status": "approved",
            "decision": "approved",
            "decision_rationale": "Good credit history",
            "approved_by": "loan_officer_1"
        },
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["id"] == loan_id
    assert updated_data["status"] == "approved"
    assert updated_data["decision"] == "approved"
    assert updated_data["decision_rationale"] == "Good credit history"
    assert updated_data["approved_by"] == "loan_officer_1"
    assert updated_data["updated_at"] > created_data["updated_at"]

    # Verify in database
    db = SessionLocal()
    loan_app = db.query(LoanApplication).filter(LoanApplication.id == loan_id).first()
    assert loan_app.status == "approved"
    assert loan_app.decision == "approved"
    db.close()

@pytest.mark.asyncio
async def test_update_loan_application_status_partial_data(client: AsyncClient):
    # Create an application
    create_response = await client.post(
        "/loan-applications/",
        json={
            "applicant_id": "applicant_partial",
            "loan_amount": 15000.0,
            "credit_score": 720,
            "income": 65000.0
        },
    )
    assert create_response.status_code == 200
    created_data = create_response.json()
    loan_id = created_data["id"]

    # Update only status and decision, leaving rationale and approved_by as None
    update_response = await client.put(
        f"/loan-applications/{loan_id}/status",
        json={
            "status": "rejected",
            "decision": "rejected",
            "decision_rationale": None,
            "approved_by": None
        },
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["id"] == loan_id
    assert updated_data["status"] == "rejected"
    assert updated_data["decision"] == "rejected"
    assert updated_data["decision_rationale"] is None
    assert updated_data["approved_by"] is None

    # Verify in database
    db = SessionLocal()
    loan_app = db.query(LoanApplication).filter(LoanApplication.id == loan_id).first()
    assert loan_app.status == "rejected"
    assert loan_app.decision == "rejected"
    assert loan_app.decision_rationale is None
    assert loan_app.approved_by is None
    db.close()

@pytest.mark.asyncio
async def test_update_nonexistent_loan_application_status(client: AsyncClient):
    response = await client.put(
        "/loan-applications/99999/status",
        json={
            "status": "approved",
            "decision": "approved",
            "decision_rationale": "Good credit history",
            "approved_by": "loan_officer_1"
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Loan application not found"}

@pytest.mark.asyncio
async def test_automated_risk_assessment_high_risk(client: AsyncClient):
    create_response = await client.post(
        "/loan-applications/",
        json={
            "applicant_id": "applicant_high_risk",
            "loan_amount": 50000.0,
            "credit_score": 500, # Low credit score
            "income": 30000.0 # Low income
        },
    )
    assert create_response.status_code == 200
    created_data = create_response.json()
    loan_id = created_data["id"]

    get_response = await client.get(f"/loan-applications/{loan_id}")
    assert get_response.status_code == 200
    retrieved_data = get_response.json()
    assert retrieved_data["risk_assessment"] == "High Risk"

@pytest.mark.asyncio
async def test_automated_risk_assessment_medium_risk(client: AsyncClient):
    create_response = await client.post(
        "/loan-applications/",
        json={
            "applicant_id": "applicant_medium_risk",
            "loan_amount": 30000.0,
            "credit_score": 600, # Medium credit score
            "income": 50000.0 # Medium income
        },
    )
    assert create_response.status_code == 200
    created_data = create_response.json()
    loan_id = created_data["id"]

    get_response = await client.get(f"/loan-applications/{loan_id}")
    assert get_response.status_code == 200
    retrieved_data = get_response.json()
    assert retrieved_data["risk_assessment"] == "Medium Risk"

@pytest.mark.asyncio
async def test_automated_risk_assessment_low_risk(client: AsyncClient):
    create_response = await client.post(
        "/loan-applications/",
        json={
            "applicant_id": "applicant_low_risk",
            "loan_amount": 10000.0,
            "credit_score": 750, # High credit score
            "income": 80000.0 # High income
        },
    )
    assert create_response.status_code == 200
    created_data = create_response.json()
    loan_id = created_data["id"]

    get_response = await client.get(f"/loan-applications/{loan_id}")
    assert get_response.status_code == 200
    retrieved_data = get_response.json()
    assert retrieved_data["risk_assessment"] == "Low Risk"

@pytest.mark.asyncio
async def test_get_loan_application_audit_logs(client: AsyncClient):
    # Create an application
    create_response = await client.post(
        "/loan-applications/",
        json={
            "applicant_id": "applicant_audit",
            "loan_amount": 10000.0,
            "credit_score": 700,
            "income": 50000.0
        },
    )
    assert create_response.status_code == 200
    created_data = create_response.json()
    loan_id = created_data["id"]

    # Update its status to approved
    await client.put(
        f"/loan-applications/{loan_id}/status",
        json={
            "status": "approved",
            "decision": "approved",
            "decision_rationale": "Good credit history",
            "approved_by": "loan_officer_1"
        },
    )

    # Get audit logs
    audit_logs_response = await client.get(f"/loan-applications/{loan_id}/audit-logs")
    assert audit_logs_response.status_code == 200
    audit_logs = audit_logs_response.json()

    assert len(audit_logs) == 2 # Created and Status Updated
    assert audit_logs[0]["action"] == "Loan Application Created"
    assert audit_logs[0]["loan_application_id"] == loan_id
    assert "Initial risk assessment" in audit_logs[0]["details"]

    assert audit_logs[1]["action"] == "Loan Application Status Updated"
    assert audit_logs[1]["loan_application_id"] == loan_id
    assert audit_logs[1]["user_id"] == "loan_officer_1"
    assert "Status changed from pending to approved" in audit_logs[1]["details"]

@pytest.mark.asyncio
async def test_get_loan_application_audit_logs_nonexistent_application(client: AsyncClient):
    response = await client.get("/loan-applications/99999/audit-logs")
    assert response.status_code == 404
    assert response.json() == {"detail": "Loan application not found"}
