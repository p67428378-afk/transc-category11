from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.models.models import RecurringPayment, Transaction, Notification, RecurringPaymentStatus, TransactionType, TransactionStatus, NotificationType, NotificationStatus, User
from app.crud import crud_recurring_payment

# Placeholder for external balance check service
def check_balance(user_id: int, amount: float) -> bool:
    """Simulates checking user's balance."""
    # In a real system, this would call an external banking API
    print(f"Checking balance for user {user_id} for amount {amount}")
    # For demonstration, let's assume user 1 always has enough funds, others don't
    if user_id == 1:
        return True
    return False

# Placeholder for external fund deduction service
def deduct_funds(user_id: int, amount: float) -> bool:
    """Simulates deducting funds from user's account."""
    # In a real system, this would call an external banking API
    print(f"Deducting {amount} from user {user_id}")
    return True # Assume deduction is always successful if balance check passed

def log_transaction(db: Session, user_id: int, recurring_payment_id: int, amount: float, transaction_type: TransactionType, status: TransactionStatus, tag: Optional[str] = None, description: Optional[str] = None) -> Transaction:
    """Logs a transaction in the database."""
    db_transaction = Transaction(
        user_id=user_id,
        recurring_payment_id=recurring_payment_id,
        type=transaction_type,
        amount=amount,
        currency="USD", # Assuming USD for now
        transaction_date=datetime.now(),
        status=status,
        tag=tag,
        description=description
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def send_notification(db: Session, user_id: int, notification_type: NotificationType, message: str, related_transaction_id: Optional[int] = None) -> Notification:
    """Sends a notification to the user."""
    db_notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
        timestamp=datetime.now(),
        status=NotificationStatus.SENT,
        related_transaction_id=related_transaction_id
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def process_recurring_payments(db: Session):
    """
    Processes all recurring payments that are due today.
    """
    today = datetime.now().date()
    due_payments = crud_recurring_payment.get_due_recurring_payments(db, today)

    for payment in due_payments:
        if payment.status != RecurringPaymentStatus.ACTIVE:
            print(f"Skipping inactive recurring payment {payment.id}")
            continue

        print(f"Processing recurring payment {payment.id} for user {payment.user_id}, amount {payment.amount}")

        # 1. Real-time balance check
        if check_balance(payment.user_id, payment.amount):
            # 2. Deduct funds
            if deduct_funds(payment.user_id, payment.amount):
                # 3. Log successful payment
                transaction = log_transaction(
                    db,
                    payment.user_id,
                    payment.id,
                    payment.amount,
                    TransactionType.DEBIT,
                    TransactionStatus.SUCCESS,
                    tag="AUTOPAY",
                    description=f"Recurring payment to {payment.biller_name}"
                )
                print(f"Successfully processed payment {payment.id}. Transaction ID: {transaction.id}")
                send_notification(
                    db,
                    payment.user_id,
                    NotificationType.PAYMENT_SUCCESS,
                    f"Your recurring payment to {payment.biller_name} of {payment.amount} {payment.currency} was successful.",
                    related_transaction_id=transaction.id
                )
            else:
                # This case should ideally not be reached if deduct_funds is reliable after check_balance
                print(f"Failed to deduct funds for payment {payment.id} after balance check.")
                transaction = log_transaction(
                    db,
                    payment.user_id,
                    payment.id,
                    payment.amount,
                    TransactionType.DEBIT,
                    TransactionStatus.FAILED,
                    description=f"Failed recurring payment to {payment.biller_name} - deduction failed"
                )
                send_notification(
                    db,
                    payment.user_id,
                    NotificationType.PAYMENT_FAILED,
                    f"Your recurring payment to {payment.biller_name} of {payment.amount} {payment.currency} failed due to an unexpected error during deduction.",
                    related_transaction_id=transaction.id
                )
        else:
            # 4. Insufficient funds - skip execution and send failure notification
            print(f"Insufficient funds for payment {payment.id}. Skipping execution.")
            transaction = log_transaction(
                db,
                payment.user_id,
                payment.id,
                payment.amount,
                TransactionType.DEBIT,
                TransactionStatus.FAILED,
                description=f"Failed recurring payment to {payment.biller_name} - insufficient funds"
            )
            send_notification(
                db,
                payment.user_id,
                NotificationType.PAYMENT_FAILED,
                f"Your recurring payment to {payment.biller_name} of {payment.amount} {payment.currency} failed due to insufficient funds.",
                related_transaction_id=transaction.id
            )
        
        # Update next payment date regardless of success or failure
        crud_recurring_payment.update_recurring_payment_next_date(db, payment)
    
    return {"message": f"Processed {len(due_payments)} recurring payments."}
