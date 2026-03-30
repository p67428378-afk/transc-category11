from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import TransactionCreate, TransactionResponse
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
