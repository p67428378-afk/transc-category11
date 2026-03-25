
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from models import Category, CategorizationRule, Transaction
from schemas import TransactionCreate
from typing import Optional, List

def get_category_for_merchant(db: Session, merchant_name: str) -> Optional[Category]:
    # 1. Try to find rules where the merchant_name starts with the rule's merchant_pattern
    # This handles cases like rule "Amazon" matching "Amazon.com"
    # and rule "Comcast" matching "Comcast Cable"
    matching_rules: List[CategorizationRule] = db.query(CategorizationRule).filter(
        func.lower(merchant_name).startswith(func.lower(CategorizationRule.merchant_pattern))
    ).order_by(CategorizationRule.priority.asc()).all()

    if matching_rules:
        best_rule = matching_rules[0]
        return db.query(Category).filter(Category.category_id == best_rule.category_id).first()

    # 2. If no prefix match, try to find rules where the merchant_name contains the rule's merchant_pattern
    # This handles cases like rule "Walmart" matching "Walmart Supercenter"
    # We must exclude the problematic catch-all pattern '%' here.
    matching_rules = db.query(CategorizationRule).filter(
        CategorizationRule.merchant_pattern != '%', # Exclude the problematic catch-all
        func.lower(merchant_name).contains(func.lower(CategorizationRule.merchant_pattern))
    ).order_by(CategorizationRule.priority.asc()).all()

    if matching_rules:
        best_rule = matching_rules[0]
        return db.query(Category).filter(Category.category_id == best_rule.category_id).first()

    # 3. If no specific or partial match, return None.
    return None

def categorize_transaction(db: Session, transaction_data: TransactionCreate) -> Transaction:
    category = get_category_for_merchant(db, transaction_data.merchant_name)

    assigned_category_id = None
    flagged_for_review = False

    if category:
        assigned_category_id = category.category_id
    else:
        # If no category found, flag for review
        flagged_for_review = True

    db_transaction = Transaction(
        external_id=transaction_data.external_id,
        merchant_name=transaction_data.merchant_name,
        amount=transaction_data.amount,
        date=transaction_data.date,
        description=transaction_data.description,
        assigned_category_id=assigned_category_id,
        manual_override=False, # Initially not manually overridden
        flagged_for_review=flagged_for_review
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
