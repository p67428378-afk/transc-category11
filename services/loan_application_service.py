
from sqlalchemy.orm import Session, joinedload
from models import LoanApplication, AuditLog, LoanHistory
from schemas import LoanApplicationCreate, LoanApplicationUpdateStatus, LoanHistoryCreate
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

        # Simulate external loan history retrieval if not provided
        simulated_loan_history_data = []
        if application.loan_history:
            simulated_loan_history_data = application.loan_history
        elif random.random() > 0.5: # 50% chance of having previous loans if not provided
            simulated_loan_history_data = [
                LoanHistoryCreate(
                    previous_loan_amount=round(random.uniform(1000, 20000), 2),
                    outstanding_balance=round(random.uniform(0, 5000), 2),
                    payment_history=random.choice(["good", "fair", "poor"])
                )
            ]

        risk_assessment = self._perform_risk_assessment(simulated_credit_score, simulated_income, application.loan_amount, simulated_loan_history_data)

        db_application = LoanApplication(
            applicant_id=application.applicant_id,
            loan_amount=application.loan_amount,
            credit_score=simulated_credit_score,
            income=simulated_income,
            risk_assessment=risk_assessment
        )
        db.add(db_application)
        db.flush() # Flush to get db_application.id before committing

        if simulated_loan_history_data:
            for lh_data in simulated_loan_history_data:
                db_loan_history = LoanHistory(
                    loan_application_id=db_application.id,
                    previous_loan_amount=lh_data.previous_loan_amount,
                    outstanding_balance=lh_data.outstanding_balance,
                    payment_history=lh_data.payment_history
                )
                db.add(db_loan_history)

        db.commit()
        db.refresh(db_application)

        # Eagerly load loan_history for the response
        db_application = db.query(LoanApplication).options(joinedload(LoanApplication.loan_history)).filter(LoanApplication.id == db_application.id).first()

        self._create_audit_log(db, db_application.id, "Loan Application Created", details=f"Initial risk assessment: {risk_assessment}")

        return db_application

    def get_loan_application(self, db: Session, application_id: int) -> LoanApplication:
        return db.query(LoanApplication).options(joinedload(LoanApplication.loan_history)).filter(LoanApplication.id == application_id).first()

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

    def _perform_risk_assessment(self, credit_score: int, income: float, loan_amount: float, loan_history: list[LoanHistoryCreate] = None) -> str:
        # Enhanced placeholder for actual risk assessment logic
        # This can be expanded to integrate with external services or more complex rules

        risk_factors = []

        # Credit Score based assessment
        if credit_score < 550:
            risk_factors.append("low_credit_score")
        elif 550 <= credit_score < 680:
            risk_factors.append("medium_credit_score")
        else:
            risk_factors.append("high_credit_score")

        # Debt-to-income ratio assessment
        if income > 0:
            dti_ratio = loan_amount / income
            if dti_ratio > 0.8:
                risk_factors.append("high_dti")
            elif dti_ratio > 0.5:
                risk_factors.append("medium_dti")
            else:
                risk_factors.append("low_dti")
        else:
            risk_factors.append("no_income_data")

        # Loan History assessment
        if loan_history:
            for lh in loan_history:
                # Access attributes using dot notation for Pydantic models
                if lh.payment_history == "poor":
                    risk_factors.append("poor_payment_history")
                elif lh.payment_history == "fair":
                    risk_factors.append("fair_payment_history")

        # Determine overall risk based on collected factors
        if "low_credit_score" in risk_factors or "high_dti" in risk_factors or "poor_payment_history" in risk_factors:
            return "High Risk"
        elif "medium_credit_score" in risk_factors or "medium_dti" in risk_factors or "fair_payment_history" in risk_factors or "no_income_data" in risk_factors:
            return "Medium Risk"
        else:
            return "Low Risk"

loan_application_service = LoanApplicationService()
