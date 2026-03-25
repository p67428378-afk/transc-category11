
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Category, CategorizationRule, Transaction
from schemas import TransactionCreate
from typing import Optional, List

def get_category_for_merchant(db: Session, merchant_name: str) -> Optional[Category]:
    # Find rules that match the merchant name, ordered by priority
    # Using ILIKE for case-insensitive matching and % for wildcard
    matching_rules: List[CategorizationRule] = db.query(CategorizationRule).filter(
        CategorizationRule.merchant_pattern.ilike(f"%{merchant_name}%")
    ).order_by(CategorizationRule.priority.asc()).all() # Lower priority number means higher priority

    # If no direct match, try more general patterns
    if not matching_rules:
        matching_rules = db.query(CategorizationRule).filter(
            or_(
                CategorizationRule.merchant_pattern.ilike(f"%{merchant_name.split()[0]}%"), # Match first word
                CategorizationRule.merchant_pattern.ilike("%") # Catch-all rule
            )
        ).order_by(CategorizationRule.priority.asc()).all()

    if matching_rules:
        # For simplicity, take the first rule. More complex logic might be needed for tie-breaking.
        # The HLD mentions priority for rule conflict resolution.
        # Assuming lower priority value means higher importance.
        best_rule = matching_rules[0]
        return db.query(Category).filter(Category.category_id == best_rule.category_id).first()
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
