from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import TransactionCreate, TransactionResponse, TransactionUpdate
from services.categorization_service import CategorizationService

router = APIRouter()

# Dependency to get the current user ID (mock for now)
def get_current_user_id():
    # In a real application, this would extract user ID from a JWT token
    return "test_user_id" # Placeholder

@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
def process_new_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id) # Placeholder for auth
):
    # In a real app, ensure current_user_id matches transaction_data.user_id or is authorized
    # For now, we'll allow processing for any user_id in the payload
    categorization_service = CategorizationService(db)
    processed_transaction = categorization_service.process_transaction(transaction_data)
    return processed_transaction

@router.put("/user/{user_id}/transactions/{transaction_id}/category", response_model=TransactionResponse)
def update_transaction_category(
    user_id: str,
    transaction_id: str,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id) # Placeholder for auth
):
    # In a real app, ensure current_user_id matches user_id from path or is authorized
    categorization_service = CategorizationService(db)
    updated_transaction = categorization_service.update_transaction_category(
        transaction_id=transaction_id,
        user_id=user_id,
        new_category=transaction_update.assigned_category
    )
    if not updated_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found or not authorized")
    return updated_transaction
