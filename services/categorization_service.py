from typing import List, Optional
from sqlalchemy.orm import Session
from models import PreseededMapping, CustomMapping, Transaction, BudgetCategory
from schemas import TransactionCreate, TransactionResponse
from datetime import datetime

class CategorizationService:
    def __init__(self, db: Session):
        self.db = db

    def _get_all_mappings(self, user_id: str) -> List[dict]:
        preseeded_mappings = self.db.query(PreseededMapping).all()
        custom_mappings = self.db.query(CustomMapping).filter(CustomMapping.user_id == user_id).all()

        all_mappings = []
        for pm in preseeded_mappings:
            all_mappings.append({
                "id": pm.preseeded_mapping_id,
                "merchant_keyword": pm.merchant_keyword.lower(),
                "category": pm.category,
                "priority": pm.priority,
                "type": "preseeded"
            })
        for cm in custom_mappings:
            all_mappings.append({
                "id": cm.custom_mapping_id,
                "merchant_keyword": cm.merchant_keyword.lower(),
                "category": cm.category,
                "priority": 1000, # Custom mappings have higher priority
                "type": "custom"
            })
        
        # Sort by priority (descending) to ensure custom mappings are checked first
        all_mappings.sort(key=lambda x: x["priority"], reverse=True)
        return all_mappings

    def categorize_transaction(self, user_id: str, merchant_name: str) -> Optional[tuple[str, str]]:
        merchant_name_lower = merchant_name.lower()
        all_mappings = self._get_all_mappings(user_id)

        for mapping in all_mappings:
            if mapping["merchant_keyword"] in merchant_name_lower:
                return mapping["category"], mapping["id"]
        
        return "Uncategorized", None

    def process_transaction(self, transaction_data: TransactionCreate) -> TransactionResponse:
        assigned_category, categorization_rule_id = self.categorize_transaction(
            transaction_data.user_id,
            transaction_data.merchant_name
        )

        db_transaction = Transaction(
            user_id=transaction_data.user_id,
            merchant_name=transaction_data.merchant_name,
            amount=transaction_data.amount,
            transaction_date=transaction_data.transaction_date,
            raw_description=transaction_data.raw_description,
            assigned_category=assigned_category,
            categorization_timestamp=datetime.now(),
            categorization_rule_id=categorization_rule_id
        )
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)

        # Update budget totals (placeholder for now)
        self._update_budget_totals(
            user_id=transaction_data.user_id,
            category=assigned_category,
            amount=transaction_data.amount
        )

        return TransactionResponse.model_validate(db_transaction)

    def _update_budget_totals(self, user_id: str, category: str, amount: int):
        # In a real scenario, this would involve an API call to the Budget Tracking Module
        # For now, we'll simulate an update to our local BudgetCategory model
        print(f"Simulating API call to Budget Tracking Module: User {user_id}, Category {category}, Amount {amount}")
        current_month = datetime.now().month
        current_year = datetime.now().year

        budget_category = self.db.query(BudgetCategory).filter(
            BudgetCategory.user_id == user_id,
            BudgetCategory.month == current_month,
            BudgetCategory.year == current_year,
            BudgetCategory.category == category
        ).first()

        if budget_category:
            budget_category.spent_amount += amount
        else:
            budget_category = BudgetCategory(
                user_id=user_id,
                month=current_month,
                year=current_year,
                category=category,
                budgeted_amount=0, # Assuming 0 if not pre-defined
                spent_amount=amount
            )
            self.db.add(budget_category)
        self.db.commit()
        self.db.refresh(budget_category)

    def update_transaction_category(self, transaction_id: str, user_id: str, new_category: str) -> Optional[Transaction]:
        db_transaction = self.db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id,
            Transaction.user_id == user_id
        ).first()

        if not db_transaction:
            return None

        old_category = db_transaction.assigned_category
        old_amount = db_transaction.amount

        # Deduct from old category budget
        if old_category != "Uncategorized":
            print(f"Simulating API call to Budget Tracking Module: Deducting {old_amount} from {old_category} for User {user_id}")
            self._update_budget_totals(user_id, old_category, -old_amount)

        # Add to new category budget
        print(f"Simulating API call to Budget Tracking Module: Adding {old_amount} to {new_category} for User {user_id}")
        self._update_budget_totals(user_id, new_category, old_amount)

        db_transaction.assigned_category = new_category
        db_transaction.categorization_timestamp = datetime.now()
        db_transaction.categorization_rule_id = None # Manual categorization, no rule ID

        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)

        return db_transaction
