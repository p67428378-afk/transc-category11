from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class CustomMapping(Base):
    __tablename__ = "custom_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    merchant_keyword = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint('user_id', 'merchant_keyword', name='_user_merchant_uc'),)

class PreseededMapping(Base):
    __tablename__ = "preseeded_mappings"

    id = Column(Integer, primary_key=True, index=True)
    merchant_keyword = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)
    priority = Column(Integer, default=0) # Higher value = higher priority

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    merchant_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    raw_description = Column(String, nullable=True)
    assigned_category = Column(String, default="Uncategorized")
    categorization_timestamp = Column(DateTime(timezone=True), onupdate=func.now())
    categorization_rule_id = Column(Integer, nullable=True) # FK to CustomMapping or PreseededMapping

class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    budgeted_amount = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0.0)

    __table_args__ = (UniqueConstraint('user_id', 'month', 'year', 'category', name='_user_month_year_category_uc'),)
