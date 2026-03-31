from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.schemas import schemas
from app.crud import crud_recurring_payment
from app.models.models import User # Assuming a way to get the current user
from app.services.payment_processor import process_recurring_payments

router = APIRouter()

# Placeholder for current user authentication - will be replaced by actual auth logic
def get_current_user(db: Session = Depends(get_db)) -> User:
    # For now, let's assume a user with ID 1 always exists for testing purposes
    # In a real application, this would involve JWT decoding, database lookup, etc.
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        # Create a dummy user if not exists for testing
        user = User(email="test@example.com", account_id="ACC123")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/recurring-payments/", response_model=schemas.RecurringPayment, status_code=status.HTTP_201_CREATED)
def create_recurring_payment(
    payment: schemas.RecurringPaymentBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Ensure the start_date is not in the past
    if payment.start_date < datetime.now(payment.start_date.tzinfo):
        raise HTTPException(status_code=400, detail="Start date cannot be in the past")

    # Create a RecurringPaymentCreate schema with the current user's ID
    payment_create = schemas.RecurringPaymentCreate(
        **payment.model_dump(),
        user_id=current_user.id
    )
    return crud_recurring_payment.create_recurring_payment(db=db, payment=payment_create)

@router.get("/recurring-payments/{payment_id}", response_model=schemas.RecurringPayment)
def read_recurring_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_payment = crud_recurring_payment.get_recurring_payment(db=db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Recurring Payment not found")
    if db_payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this recurring payment")
    return db_payment

@router.get("/recurring-payments/", response_model=List[schemas.RecurringPayment])
def read_recurring_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payments = crud_recurring_payment.get_recurring_payments_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return payments

@router.put("/recurring-payments/{payment_id}", response_model=schemas.RecurringPayment)
def update_recurring_payment(
    payment_id: int,
    payment: schemas.RecurringPaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_payment = crud_recurring_payment.get_recurring_payment(db=db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Recurring Payment not found")
    if db_payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this recurring payment")
    
    # Ensure the start_date is not in the past if it's being updated
    if payment.start_date and payment.start_date < datetime.now(payment.start_date.tzinfo):
        raise HTTPException(status_code=400, detail="Start date cannot be in the past")

    return crud_recurring_payment.update_recurring_payment(db=db, payment_id=payment_id, payment_update=payment)

@router.delete("/recurring-payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_payment = crud_recurring_payment.get_recurring_payment(db=db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Recurring Payment not found")
    if db_payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this recurring payment")
    crud_recurring_payment.delete_recurring_payment(db=db, payment_id=payment_id)
    return {"message": "Recurring Payment deleted successfully"}

@router.post("/recurring-payments/process-due", status_code=status.HTTP_200_OK)
def process_due_recurring_payments(
    db: Session = Depends(get_db)
):
    """Manually trigger processing of all recurring payments due today."""
    return process_recurring_payments(db)
