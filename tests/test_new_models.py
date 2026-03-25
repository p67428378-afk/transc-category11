import pytest
from sqlalchemy.orm import Session
from app.models import LoanApplication, Kyc, CreditCheck, Employment, Collateral, Document
import uuid
import datetime

def test_create_credit_check(session: Session):
    applicant_id = str(uuid.uuid4())
    kyc_data = Kyc(
        applicant_id=applicant_id,
        first_name="Credit", last_name="User", date_of_birth="1990-01-01",
        address="123 Credit St", ssn="111-11-111", identification_document_id=None
    )
    session.add(kyc_data)
    session.commit()
    session.refresh(kyc_data)

    credit_check = CreditCheck(
        applicant_id=applicant_id,
        credit_score=750.0,
        bureau_source="Experian"
    )
    session.add(credit_check)
    session.commit()
    session.refresh(credit_check)

    assert credit_check.credit_check_id is not None
    assert credit_check.kyc.first_name == "Credit"

def test_create_employment(session: Session):
    applicant_id = str(uuid.uuid4())
    kyc_data = Kyc(
        applicant_id=applicant_id,
        first_name="Employ", last_name="User", date_of_birth="1990-01-01",
        address="123 Employ St", ssn="222-22-222", identification_document_id=None
    )
    session.add(kyc_data)
    session.commit()
    session.refresh(kyc_data)

    employment = Employment(
        applicant_id=applicant_id,
        employer_name="Tech Corp",
        job_title="Software Engineer",
        annual_income=120000.0
    )
    session.add(employment)
    session.commit()
    session.refresh(employment)

    assert employment.employment_id is not None
    assert employment.kyc.first_name == "Employ"

def test_create_collateral(session: Session):
    application_id = str(uuid.uuid4())
    loan_app = LoanApplication(
        application_id=application_id,
        applicant_id=str(uuid.uuid4()), # Dummy applicant_id
        loan_type="Mortgage",
        amount_requested=300000.0
    )
    session.add(loan_app)
    session.commit()
    session.refresh(loan_app)

    collateral = Collateral(
        loan_application_id=application_id,
        type="Real Estate",
        value=400000.0
    )
    session.add(collateral)
    session.commit()
    session.refresh(collateral)

    assert collateral.collateral_id is not None
    assert collateral.loan_application.loan_type == "Mortgage"

def test_loan_application_with_all_relations(session: Session):
    applicant_id = str(uuid.uuid4())
    kyc_data = Kyc(
        applicant_id=applicant_id,
        first_name="Full", last_name="App", date_of_birth="1980-01-01",
        address="789 Relation Rd", ssn="333-33-333", identification_document_id=None
    )
    session.add(kyc_data)
    session.commit()
    session.refresh(kyc_data)

    loan_app = LoanApplication(
        applicant_id=applicant_id,
        loan_type="Business Loan",
        amount_requested=50000.0
    )
    session.add(loan_app)
    session.commit()
    session.refresh(loan_app)

    credit_check = CreditCheck(
        applicant_id=applicant_id,
        loan_application_id=loan_app.application_id,
        credit_score=800.0,
        bureau_source="TransUnion"
    )
    employment = Employment(
        applicant_id=applicant_id,
        loan_application_id=loan_app.application_id,
        employer_name="Global Inc",
        job_title="CEO",
        annual_income=500000.0
    )
    collateral = Collateral(
        loan_application_id=loan_app.application_id,
        type="Stocks",
        value=100000.0
    )
    session.add_all([credit_check, employment, collateral])
    session.commit()
    session.refresh(loan_app)

    assert len(loan_app.credit_checks) == 1
    assert loan_app.credit_checks[0].credit_score == 800.0
    assert len(loan_app.employments) == 1
    assert loan_app.employments[0].employer_name == "Global Inc"
    assert len(loan_app.collaterals) == 1
    assert loan_app.collaterals[0].value == 100000.0

    assert len(kyc_data.credit_checks) == 1
    assert kyc_data.credit_checks[0].credit_score == 800.0
    assert len(kyc_data.employments) == 1
    assert kyc_data.employments[0].employer_name == "Global Inc"
