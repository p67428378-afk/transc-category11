import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from services.categorization_service import CategorizationService
from models import Transaction, BudgetCategory, CustomMapping, PreseededMapping
from schemas import TransactionCreate, TransactionUpdate

@pytest.fixture
def categorization_service(session: Session):
    return CategorizationService(session)

@pytest.fixture
def setup_transactions_and_budgets(session: Session):
    # Clear existing data
    session.query(Transaction).delete()
    session.query(BudgetCategory).delete()
    session.query(CustomMapping).delete()
    session.query(PreseededMapping).delete()
    session.commit()

    # Pre-seeded mapping
    preseeded_mapping = PreseededMapping(
        merchant_keyword="Netflix",
        category="Entertainment",
        priority=10
    )
    session.add(preseeded_mapping)
    session.commit()
    session.refresh(preseeded_mapping)

    # Custom mapping
    custom_mapping = CustomMapping(
        user_id="test_user_id",
        merchant_keyword="Local Cafe",
        category="Dining"
    )
    session.add(custom_mapping)
    session.commit()
    session.refresh(custom_mapping)

    # Initial transaction
    transaction_data = TransactionCreate(
        user_id="test_user_id",
        merchant_name="Netflix Subscription",
        amount=15,
        transaction_date=datetime.now(),
        raw_description="Monthly Netflix"
    )
    service = CategorizationService(session)
    processed_transaction = service.process_transaction(transaction_data)

    # Initial budget category for Entertainment
    budget_entertainment = BudgetCategory(
        user_id="test_user_id",
        month=datetime.now().month,
        year=datetime.now().year,
        category="Entertainment",
        budgeted_amount=100,
        spent_amount=15
    )
    session.add(budget_entertainment)
    session.commit()
    session.refresh(budget_entertainment)

    return processed_transaction, budget_entertainment

def test_update_transaction_category_success(categorization_service: CategorizationService, session: Session, setup_transactions_and_budgets):
    initial_transaction, initial_budget = setup_transactions_and_budgets

    # Verify initial state
    assert initial_transaction.assigned_category == "Entertainment"
    assert initial_budget.spent_amount == 15

    # Update category to "Utilities"
    new_category = "Utilities"
    updated_transaction = categorization_service.update_transaction_category(
        transaction_id=initial_transaction.transaction_id,
        user_id="test_user_id",
        new_category=new_category
    )

    assert updated_transaction is not None
    assert updated_transaction.assigned_category == new_category
    assert updated_transaction.categorization_rule_id is None

    # Verify old budget category is updated (spent_amount reduced)
    old_budget_category = session.query(BudgetCategory).filter(
        BudgetCategory.user_id == "test_user_id",
        BudgetCategory.month == datetime.now().month,
        BudgetCategory.year == datetime.now().year,
        BudgetCategory.category == "Entertainment"
    ).first()
    assert old_budget_category.spent_amount == 0  # 15 - 15 = 0

    # Verify new budget category is created/updated (spent_amount increased)
    new_budget_category = session.query(BudgetCategory).filter(
        BudgetCategory.user_id == "test_user_id",
        BudgetCategory.month == datetime.now().month,
        BudgetCategory.year == datetime.now().year,
        BudgetCategory.category == new_category
    ).first()
    assert new_budget_category.spent_amount == 15

def test_update_transaction_category_not_found(categorization_service: CategorizationService):
    updated_transaction = categorization_service.update_transaction_category(
        transaction_id="non_existent_id",
        user_id="test_user_id",
        new_category="Groceries"
    )
    assert updated_transaction is None

def test_update_budget_totals_existing_category(categorization_service: CategorizationService, session: Session):
    user_id = "user_budget_test"
    category = "Food"
    amount = 50
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Create an initial budget category
    initial_budget = BudgetCategory(
        user_id=user_id,
        month=current_month,
        year=current_year,
        category=category,
        budgeted_amount=200,
        spent_amount=30
    )
    session.add(initial_budget)
    session.commit()
    session.refresh(initial_budget)

    categorization_service._update_budget_totals(user_id, category, amount)

    updated_budget = session.query(BudgetCategory).filter(
        BudgetCategory.user_id == user_id,
        BudgetCategory.month == current_month,
        BudgetCategory.year == current_year,
        BudgetCategory.category == category
    ).first()

    assert updated_budget.spent_amount == 80 # 30 + 50

def test_update_budget_totals_new_category(categorization_service: CategorizationService, session: Session):
    user_id = "user_new_budget_test"
    category = "Travel"
    amount = 100
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Ensure category does not exist initially
    existing_budget = session.query(BudgetCategory).filter(
        BudgetCategory.user_id == user_id,
        BudgetCategory.month == current_month,
        BudgetCategory.year == current_year,
        BudgetCategory.category == category
    ).first()
    assert existing_budget is None

    categorization_service._update_budget_totals(user_id, category, amount)

    new_budget = session.query(BudgetCategory).filter(
        BudgetCategory.user_id == user_id,
        BudgetCategory.month == current_month,
        BudgetCategory.year == current_year,
        BudgetCategory.category == category
    ).first()

    assert new_budget is not None
    assert new_budget.spent_amount == 100
    assert new_budget.budgeted_amount == 0 # Default value
