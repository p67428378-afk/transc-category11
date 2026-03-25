
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Category, CategorizationRule, Transaction, ReportedIssue
from schemas import (
    CategoryCreate, CategoryResponse,
    CategorizationRuleCreate, CategorizationRuleResponse,
    TransactionCreate, TransactionResponse, TransactionUpdateCategory,
    ReportedIssueCreate, ReportedIssueResponse
)
from services.categorization_service import categorize_transaction, get_category_for_merchant
from typing import List

router = APIRouter()

@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(category_name=category.category_name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.post("/rules/", response_model=CategorizationRuleResponse, status_code=status.HTTP_200_OK)
def create_categorization_rule(rule: CategorizationRuleCreate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.category_id == rule.category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_rule = CategorizationRule(
        merchant_pattern=rule.merchant_pattern,
        category_id=rule.category_id,
        priority=rule.priority
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.post("/transactions/categorize", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
def create_and_categorize_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = categorize_transaction(db, transaction)
    # Eagerly load the assigned_category relationship
    db.refresh(db_transaction, attribute_names=["assigned_category"])
    return db_transaction

@router.get("/transactions/", response_model=List[TransactionResponse], status_code=status.HTTP_200_OK)
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).options(joinedload(Transaction.assigned_category)).all()
    return transactions

@router.put("/transactions/{transaction_id}/recategorize", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
def recategorize_transaction(
    transaction_id: str, new_category: TransactionUpdateCategory, db: Session = Depends(get_db)
):
    db_transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db_category = db.query(Category).filter(Category.category_id == new_category.assigned_category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="New category not found")

    db_transaction.assigned_category_id = new_category.assigned_category_id
    db_transaction.manual_override = True
    db_transaction.flagged_for_review = False # If manually recategorized, it's no longer flagged
    db.commit()
    db.refresh(db_transaction, attribute_names=["assigned_category"])
    return db_transaction

@router.post("/transactions/{transaction_id}/report", response_model=ReportedIssueResponse, status_code=status.HTTP_200_OK)
def report_incorrect_categorization(
    transaction_id: str, issue: ReportedIssueCreate, db: Session = Depends(get_db)
):
    db_transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db_issue = ReportedIssue(
        transaction_id=transaction_id,
        reported_by_user_id=issue.reported_by_user_id,
        issue_description=issue.issue_description,
        status=issue.status
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue
