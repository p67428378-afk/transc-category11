import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class PreseededMapping(Base):
    __tablename__ = "preseeded_mappings"

    preseeded_mapping_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_keyword = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)
    priority = Column(Integer, default=0)

    def __repr__(self):
        return f"<PreseededMapping(merchant_keyword='{self.merchant_keyword}', category='{self.category}')>"

class CustomMapping(Base):
    __tablename__ = "custom_mappings"

    custom_mapping_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    merchant_keyword = Column(String, nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        {
            "unique_together": ("user_id", "merchant_keyword"),
        }
    )

    def __repr__(self):
        return f"<CustomMapping(user_id='{self.user_id}', merchant_keyword='{self.merchant_keyword}', category='{self.category}')>"

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    merchant_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    raw_description = Column(String)
    assigned_category = Column(String, default="Uncategorized")
    categorization_timestamp = Column(DateTime, onupdate=func.now())
    categorization_rule_id = Column(String, nullable=True) # FK to CustomMapping or PreseededMapping

    def __repr__(self):
        return f"<Transaction(merchant_name='{self.merchant_name}', assigned_category='{self.assigned_category}')>"

class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    budget_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    budgeted_amount = Column(Integer, default=0)
    spent_amount = Column(Integer, default=0)

    __table_args__ = (
        {
            "unique_together": ("user_id", "month", "year", "category"),
        }
    )

    def __repr__(self):
        return f"<BudgetCategory(user_id='{self.user_id}', category='{self.category}', spent_amount='{self.spent_amount}')>"
