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

class Kyc(Base):
    __tablename__ = "kyc"

    applicant_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(String) # Storing as string for simplicity, can be Date type
    address = Column(String)
    ssn = Column(String) # Encrypted in real scenario
    identification_document_id = Column(String, ForeignKey("documents.document_id"))

    loan_application = relationship("LoanApplication", back_populates="kyc")
    identification_document = relationship("Document", foreign_keys=[identification_document_id])

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    loan_application_id = Column(String, ForeignKey("loan_applications.application_id"))
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
