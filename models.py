
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    category_name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    rules = relationship("CategorizationRule", back_populates="category")
    transactions = relationship("Transaction", back_populates="assigned_category")

class CategorizationRule(Base):
    __tablename__ = "categorization_rules"

    rule_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    merchant_pattern = Column(String, index=True, nullable=False)
    category_id = Column(String, ForeignKey("categories.category_id"), nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="rules")

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(String, unique=True, index=True, nullable=False)
    merchant_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String, nullable=True)
    assigned_category_id = Column(String, ForeignKey("categories.category_id"), nullable=True)
    manual_override = Column(Boolean, default=False)
    flagged_for_review = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assigned_category = relationship("Category", back_populates="transactions")
    reported_issues = relationship("ReportedIssue", back_populates="transaction")

class ReportedIssue(Base):
    __tablename__ = "reported_issues"

    issue_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, ForeignKey("transactions.transaction_id"), nullable=False)
    reported_by_user_id = Column(String, nullable=False)
    issue_description = Column(String, nullable=True)
    status = Column(String, default="Open", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    transaction = relationship("Transaction", back_populates="reported_issues")
