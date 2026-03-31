
from sqlalchemy.orm import Session
from models import LoanApplication, AuditLog
from schemas import LoanApplicationCreate, LoanApplicationUpdateStatus
from datetime import datetime, timezone
import random

class LoanApplicationService:
    def _create_audit_log(self, db: Session, loan_application_id: int, action: str, user_id: str = None, details: str = None):
        audit_log = AuditLog(
            loan_application_id=loan_application_id,
            action=action,
            user_id=user_id,
            details=details
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

    def create_loan_application(self, db: Session, application: LoanApplicationCreate) -> LoanApplication:
        # Simulate external credit score and income verification
        simulated_credit_score = application.credit_score if application.credit_score is not None else random.randint(300, 850)
        simulated_income = application.income if application.income is not None else round(random.uniform(20000, 150000), 2)

        risk_assessment = self._perform_risk_assessment(simulated_credit_score, simulated_income, application.loan_amount)

        db_application = LoanApplication(
            applicant_id=application.applicant_id,
            loan_amount=application.loan_amount,
            credit_score=simulated_credit_score,
            income=simulated_income,
            risk_assessment=risk_assessment
        )
        db.add(db_application)
        db.commit()
        db.refresh(db_application)

        self._create_audit_log(db, db_application.id, "Loan Application Created", details=f"Initial risk assessment: {risk_assessment}")

        return db_application

    def get_loan_application(self, db: Session, application_id: int) -> LoanApplication:
        return db.query(LoanApplication).filter(LoanApplication.id == application_id).first()

    def get_audit_logs_for_application(self, db: Session, loan_application_id: int) -> list[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.loan_application_id == loan_application_id).order_by(AuditLog.timestamp.asc()).all()

    def update_loan_application_status(self, db: Session, application_id: int, update_data: LoanApplicationUpdateStatus) -> LoanApplication:
        db_application = self.get_loan_application(db, application_id)
        if db_application:
            old_status = db_application.status
            db_application.status = update_data.status
            db_application.decision = update_data.decision
            db_application.decision_rationale = update_data.decision_rationale
            db_application.approved_by = update_data.approved_by
            db_application.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(db_application)

            details = f"Status changed from {old_status} to {update_data.status}. Decision: {update_data.decision}. Rationale: {update_data.decision_rationale}"
            self._create_audit_log(db, db_application.id, "Loan Application Status Updated", user_id=update_data.approved_by, details=details)

        return db_application

    def _perform_risk_assessment(self, credit_score: int, income: float, loan_amount: float) -> str:
        # Enhanced placeholder for actual risk assessment logic
        # This can be expanded to integrate with external services or more complex rules

        # Rule 1: Very low credit score or extremely high debt-to-income ratio
        if credit_score < 550 or (income > 0 and (loan_amount / income) > 0.8): # Loan amount is 80% of annual income
            return "High Risk"

        # Rule 2: Moderate credit score or high debt-to-income ratio
        if 550 <= credit_score < 680 or (income > 0 and (loan_amount / income) > 0.5): # Loan amount is 50% of annual income
            return "Medium Risk"

        # Rule 3: Good credit score and manageable debt-to-income ratio
        if credit_score >= 680 and (income > 0 and (loan_amount / income) <= 0.5):
            return "Low Risk"

        # Default case if none of the above rules match (e.g., income is 0 or other edge cases)
        return "Medium Risk" # A neutral default if specific rules don't apply

loan_application_service = LoanApplicationService()
