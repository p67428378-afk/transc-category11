from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime
import uuid

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    application_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    applicant_id = Column(String, ForeignKey("kyc.applicant_id"))
    loan_type = Column(String, index=True)
    amount_requested = Column(Float)
    status = Column(String, default="Pending")
    submission_date = Column(DateTime, default=datetime.datetime.utcnow)
    decision_date = Column(DateTime, nullable=True)
    risk_score = Column(Float, nullable=True)
    compliance_status = Column(String, nullable=True)
    loan_officer_id = Column(String, nullable=True) # FK to User/Loan Officer, assuming string for now
    comments = Column(String, nullable=True)

    kyc = relationship("Kyc", back_populates="loan_application", uselist=False)
    documents = relationship("Document", back_populates="loan_application")
    audit_trails = relationship("AuditTrail", back_populates="loan_application")
    credit_checks = relationship("CreditCheck", back_populates="loan_application")
    employments = relationship("Employment", back_populates="loan_application")
    collaterals = relationship("Collateral", back_populates="loan_application")

class Kyc(Base):
    __tablename__ = "kyc"

    applicant_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(String) # Storing as string for simplicity, can be Date type
    address = Column(String)
    ssn = Column(String) # Encrypted in real scenario
    identification_document_id = Column(String, ForeignKey("documents.document_id"), nullable=True)

    loan_application = relationship("LoanApplication", back_populates="kyc")
    identification_document = relationship("Document", foreign_keys=[identification_document_id])
    credit_checks = relationship("CreditCheck", back_populates="kyc")
    employments = relationship("Employment", back_populates="kyc")

class CreditCheck(Base):
    __tablename__ = "credit_checks"

    credit_check_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    applicant_id = Column(String, ForeignKey("kyc.applicant_id"))
    loan_application_id = Column(String, ForeignKey("loan_applications.application_id"), nullable=True)
    credit_score = Column(Float)
    credit_report_id = Column(String, ForeignKey("documents.document_id"), nullable=True)
    report_date = Column(DateTime, default=datetime.datetime.utcnow)
    bureau_source = Column(String)

    kyc = relationship("Kyc", back_populates="credit_checks")
    loan_application = relationship("LoanApplication", back_populates="credit_checks")
    credit_report = relationship("Document", foreign_keys=[credit_report_id])

class Employment(Base):
    __tablename__ = "employments"

    employment_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    applicant_id = Column(String, ForeignKey("kyc.applicant_id"))
    loan_application_id = Column(String, ForeignKey("loan_applications.application_id"), nullable=True)
    employer_name = Column(String)
    job_title = Column(String)
    annual_income = Column(Float)
    income_verification_document_id = Column(String, ForeignKey("documents.document_id"), nullable=True)

    kyc = relationship("Kyc", back_populates="employments")
    loan_application = relationship("LoanApplication", back_populates="employments")
    income_verification_document = relationship("Document", foreign_keys=[income_verification_document_id])

class Collateral(Base):
    __tablename__ = "collaterals"

    collateral_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    loan_application_id = Column(String, ForeignKey("loan_applications.application_id"))
    type = Column(String)
    value = Column(Float)
    document_id = Column(String, ForeignKey("documents.document_id"), nullable=True)

    loan_application = relationship("LoanApplication", back_populates="collaterals")
    document = relationship("Document", foreign_keys=[document_id])

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    loan_application_id = Column(String, ForeignKey("loan_applications.application_id"), nullable=True)
    type = Column(String)
    storage_path = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)

    loan_application = relationship("LoanApplication", back_populates="documents")

class AuditTrail(Base):
    __tablename__ = "audit_trails"

    audit_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    loan_application_id = Column(String, ForeignKey("loan_applications.application_id"))
    action = Column(String)
    user_id = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(String, nullable=True) # JSON blob for additional context

    loan_application = relationship("LoanApplication", back_populates="audit_trails")
