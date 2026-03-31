
import pytest
from unittest.mock import MagicMock, patch
from services.loan_application_service import LoanApplicationService
from schemas import LoanApplicationCreate, LoanApplicationUpdateStatus
from models import LoanApplication, AuditLog
from datetime import datetime, timezone

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def loan_application_service_instance():
    return LoanApplicationService()

def test_create_audit_log(mock_db_session, loan_application_service_instance):
    loan_application_service_instance._create_audit_log(mock_db_session, 1, "Test Action", "test_user", "Test Details")
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

@patch('services.loan_application_service.random')
def test_create_loan_application_service_with_audit_log(mock_random, mock_db_session, loan_application_service_instance):
    mock_random.randint.return_value = 700
    mock_random.uniform.return_value = 50000.0

    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.side_effect = lambda x: x

    application_create = LoanApplicationCreate(
        applicant_id="test_applicant",
        loan_amount=10000.0,
        credit_score=None,
        income=None
    )

    loan_app = loan_application_service_instance.create_loan_application(mock_db_session, application_create)

    assert loan_app.applicant_id == "test_applicant"
    assert loan_app.credit_score == 700
    assert loan_app.income == 50000.0
    assert loan_app.risk_assessment == "Low Risk"

    # Verify audit log creation
    assert mock_db_session.add.call_count == 2  # One for LoanApplication, one for AuditLog
    assert mock_db_session.commit.call_count == 2
    assert mock_db_session.refresh.call_count == 2

def test_get_loan_application_service(mock_db_session, loan_application_service_instance):
    mock_loan_app = LoanApplication(
        id=1,
        applicant_id="test_applicant",
        loan_amount=10000.0,
        credit_score=700,
        income=50000.0,
        status="pending",
        risk_assessment="Low Risk",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_loan_app

    retrieved_app = loan_application_service_instance.get_loan_application(mock_db_session, 1)

    assert retrieved_app.id == 1
    assert retrieved_app.applicant_id == "test_applicant"
    mock_db_session.query.assert_called_once_with(LoanApplication)

def test_get_loan_application_service_not_found(mock_db_session, loan_application_service_instance):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    retrieved_app = loan_application_service_instance.get_loan_application(mock_db_session, 999)

    assert retrieved_app is None

def test_update_loan_application_status_service_with_audit_log(mock_db_session, loan_application_service_instance):
    initial_app = LoanApplication(
        id=1,
        applicant_id="test_applicant",
        loan_amount=10000.0,
        credit_score=700,
        income=50000.0,
        status="pending",
        risk_assessment="Low Risk",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = initial_app
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.side_effect = lambda x: x

    update_data = LoanApplicationUpdateStatus(
        status="approved",
        decision="approved",
        decision_rationale="Good credit",
        approved_by="loan_officer_1"
    )

    updated_app = loan_application_service_instance.update_loan_application_status(mock_db_session, 1, update_data)

    assert updated_app.status == "approved"
    assert updated_app.decision == "approved"
    assert updated_app.decision_rationale == "Good credit"
    assert updated_app.approved_by == "loan_officer_1"
    assert mock_db_session.commit.call_count == 2 # One for LoanApplication, one for AuditLog
    assert mock_db_session.refresh.call_count == 2

def test_update_loan_application_status_service_not_found(mock_db_session, loan_application_service_instance):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    update_data = LoanApplicationUpdateStatus(
        status="approved",
        decision="approved",
        decision_rationale="Good credit",
        approved_by="loan_officer_1"
    )

    updated_app = loan_application_service_instance.update_loan_application_status(mock_db_session, 999, update_data)

    assert updated_app is None
    mock_db_session.commit.assert_not_called()
    mock_db_session.refresh.assert_not_called()

@pytest.mark.parametrize("credit_score, income, loan_amount, expected_risk", [
    (500, 30000.0, 50000.0, "High Risk"), # credit < 550
    (600, 30000.0, 25000.0, "High Risk"), # loan/income > 0.8
    (700, 80000.0, 10000.0, "Low Risk"), # credit >= 680 and loan/income <= 0.5
    (600, 10000.0, 8000.0, "Medium Risk"), # 550 <= credit < 680 or loan/income > 0.5
    (600, 10000.0, 6000.0, "Medium Risk"), # 550 <= credit < 680 or loan/income > 0.5
    (600, 10000.0, 4000.0, "Medium Risk"), # 550 <= credit < 680 and loan/income <= 0.5
    (700, 0.0, 10000.0, "Medium Risk"), # income is 0, default to Medium Risk
    (700, 50000.0, 0.0, "Low Risk"), # loan_amount is 0
])
def test_perform_risk_assessment(loan_application_service_instance, credit_score, income, loan_amount, expected_risk):
    risk = loan_application_service_instance._perform_risk_assessment(credit_score, income, loan_amount)
    assert risk == expected_risk

def test_get_audit_logs_for_application(mock_db_session, loan_application_service_instance):
    mock_audit_log_1 = AuditLog(
        id=1,
        loan_application_id=1,
        action="Created",
        timestamp=datetime.now(timezone.utc),
        user_id="system",
        details="App created"
    )
    mock_audit_log_2 = AuditLog(
        id=2,
        loan_application_id=1,
        action="Status Updated",
        timestamp=datetime.now(timezone.utc),
        user_id="loan_officer_1",
        details="Status changed to approved"
    )
    mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        mock_audit_log_1, mock_audit_log_2
    ]

    audit_logs = loan_application_service_instance.get_audit_logs_for_application(mock_db_session, 1)

    assert len(audit_logs) == 2
    assert audit_logs[0].action == "Created"
    assert audit_logs[1].action == "Status Updated"
    mock_db_session.query.assert_called_once_with(AuditLog)
