
from sqlalchemy.orm import Session
from models import LoanApplication
from schemas import LoanApplicationCreate, LoanApplicationUpdateStatus
from datetime import datetime, timezone

class LoanApplicationService:
    def create_loan_application(self, db: Session, application: LoanApplicationCreate) -> LoanApplication:
        # Simple risk assessment logic (can be expanded)
        risk_assessment = self._perform_risk_assessment(application.credit_score, application.income, application.loan_amount)

        db_application = LoanApplication(
            applicant_id=application.applicant_id,
            loan_amount=application.loan_amount,
            credit_score=application.credit_score,
            income=application.income,
            risk_assessment=risk_assessment
        )
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        return db_application

    def get_loan_application(self, db: Session, application_id: int) -> LoanApplication:
        return db.query(LoanApplication).filter(LoanApplication.id == application_id).first()

    def update_loan_application_status(self, db: Session, application_id: int, update_data: LoanApplicationUpdateStatus) -> LoanApplication:
        db_application = self.get_loan_application(db, application_id)
        if db_application:
            db_application.status = update_data.status
            db_application.decision = update_data.decision
            db_application.decision_rationale = update_data.decision_rationale
            db_application.approved_by = update_data.approved_by
            db_application.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(db_application)
        return db_application

    def _perform_risk_assessment(self, credit_score: int | None, income: float | None, loan_amount: float) -> str:
        # Placeholder for actual risk assessment logic
        # This can be expanded to integrate with external services or more complex rules
        if credit_score is None or income is None:
            return "High Risk" # Default to high risk if data is missing

        if credit_score < 650 or (income * 5 < loan_amount):
            return "High Risk"
        elif 650 <= credit_score <= 700 or (income * 3 < loan_amount):
            return "Medium Risk"
        else:
            return "Low Risk"

loan_application_service = LoanApplicationService()
