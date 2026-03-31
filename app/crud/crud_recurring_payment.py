from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.models.models import RecurringPayment, User, Frequency, RecurringPaymentStatus
from app.schemas.schemas import RecurringPaymentCreate, RecurringPaymentUpdate

def calculate_next_payment_date(start_date: datetime, frequency: Frequency) -> datetime:
    if frequency == Frequency.WEEKLY:
        return start_date + timedelta(weeks=1)
    elif frequency == Frequency.MONTHLY:
        # This is a simplified calculation. For production, consider day of month logic.
        # For now, just add 30 days as a placeholder.
        return start_date + timedelta(days=30)
    return start_date # Should not happen

def create_recurring_payment(db: Session, payment: RecurringPaymentCreate) -> RecurringPayment:
    next_payment_date = calculate_next_payment_date(payment.start_date, payment.frequency)
    db_payment = RecurringPayment(
        user_id=payment.user_id,
        biller_name=payment.biller_name,
        amount=payment.amount,
        currency=payment.currency,
        start_date=payment.start_date,
        frequency=payment.frequency,
        next_payment_date=next_payment_date,
        status=RecurringPaymentStatus.ACTIVE
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_recurring_payment(db: Session, payment_id: int) -> Optional[RecurringPayment]:
    return db.query(RecurringPayment).filter(RecurringPayment.id == payment_id).first()

def get_recurring_payments_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[RecurringPayment]:
    return db.query(RecurringPayment).filter(RecurringPayment.user_id == user_id).offset(skip).limit(limit).all()

def update_recurring_payment(db: Session, payment_id: int, payment_update: RecurringPaymentUpdate) -> Optional[RecurringPayment]:
    db_payment = db.query(RecurringPayment).filter(RecurringPayment.id == payment_id).first()
    if db_payment:
        update_data = payment_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_payment, key, value)
        
        # Recalculate next_payment_date if frequency or start_date changes
        if "frequency" in update_data or "start_date" in update_data:
            db_payment.next_payment_date = calculate_next_payment_date(db_payment.start_date, db_payment.frequency)

        db.commit()
        db.refresh(db_payment)
    return db_payment

def delete_recurring_payment(db: Session, payment_id: int) -> Optional[RecurringPayment]:
    db_payment = db.query(RecurringPayment).filter(RecurringPayment.id == payment_id).first()
    if db_payment:
        db.delete(db_payment)
        db.commit()
    return db_payment
