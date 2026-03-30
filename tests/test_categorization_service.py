import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import PreseededMapping, CustomMapping, Transaction, BudgetCategory
from schemas import TransactionCreate
from services.categorization_service import CategorizationService
from datetime import datetime

def test_categorize_with_preseeded_mapping(client: TestClient, session: Session):
    # Setup pre-seeded mapping
    preseeded_mapping = PreseededMapping(merchant_keyword="Netflix", category="Entertainment", priority=10)
    session.add(preseeded_mapping)
    session.commit()
    session.refresh(preseeded_mapping)

    service = CategorizationService(session)
    category, rule_id = service.categorize_transaction("user1", "Netflix Subscription")
    assert category == "Entertainment"
    assert rule_id == preseeded_mapping.preseeded_mapping_id

def test_categorize_with_custom_mapping_priority(client: TestClient, session: Session):
    user_id = "user2"
    # Setup pre-seeded mapping
    preseeded_mapping = PreseededMapping(merchant_keyword="Starbucks", category="Coffee", priority=10)
    session.add(preseeded_mapping)
    # Setup custom mapping with higher priority
    custom_mapping = CustomMapping(user_id=user_id, merchant_keyword="Starbucks", category="Work Expenses")
    session.add(custom_mapping)
    session.commit()
    session.refresh(preseeded_mapping)
    session.refresh(custom_mapping)

    service = CategorizationService(session)
    category, rule_id = service.categorize_transaction(user_id, "Starbucks Coffee")
    assert category == "Work Expenses"
    assert rule_id == custom_mapping.custom_mapping_id

def test_categorize_uncategorized_transaction(client: TestClient, session: Session):
    service = CategorizationService(session)
    category, rule_id = service.categorize_transaction("user3", "Unknown Merchant XYZ")
    assert category == "Uncategorized"
    assert rule_id is None

def test_process_transaction_api_endpoint(client: TestClient, session: Session):
    user_id = "user4"
    # Setup pre-seeded mapping
    preseeded_mapping = PreseededMapping(merchant_keyword="Amazon", category="Shopping", priority=10)
    session.add(preseeded_mapping)
    session.commit()
    session.refresh(preseeded_mapping)

    transaction_data = {
        "user_id": user_id,
        "merchant_name": "Amazon Purchase",
        "amount": 5000,
        "transaction_date": datetime.now().isoformat(),
        "raw_description": "Kindle book"
    }

    response = client.post("/api/v1/transactions", json=transaction_data)
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_category"] == "Shopping"
    assert data["user_id"] == user_id
    assert "transaction_id" in data

    # Verify transaction in DB
    db_transaction = session.query(Transaction).filter(Transaction.transaction_id == data["transaction_id"]).first()
    assert db_transaction is not None
    assert db_transaction.assigned_category == "Shopping"

    # Verify budget update in DB
    current_month = datetime.now().month
    current_year = datetime.now().year
    budget_category = session.query(BudgetCategory).filter(
        BudgetCategory.user_id == user_id,
        BudgetCategory.month == current_month,
        BudgetCategory.year == current_year,
        BudgetCategory.category == "Shopping"
    ).first()
    assert budget_category is not None
    assert budget_category.spent_amount == 5000

def test_process_transaction_uncategorized_api_endpoint(client: TestClient, session: Session):
    user_id = "user5"
    transaction_data = {
        "user_id": user_id,
        "merchant_name": "Totally New Store",
        "amount": 1000,
        "transaction_date": datetime.now().isoformat(),
        "raw_description": "Some purchase"
    }

    response = client.post("/api/v1/transactions", json=transaction_data)
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_category"] == "Uncategorized"
    assert data["user_id"] == user_id

    # Verify budget update for uncategorized (should create a budget entry with spent_amount)
    current_month = datetime.now().month
    current_year = datetime.now().year
    budget_category = session.query(BudgetCategory).filter(
        BudgetCategory.user_id == user_id,
        BudgetCategory.month == current_month,
        BudgetCategory.year == current_year,
        BudgetCategory.category == "Uncategorized"
    ).first()
    assert budget_category is not None
    assert budget_category.spent_amount == 1000
