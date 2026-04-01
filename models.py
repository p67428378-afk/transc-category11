from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
from database import Base
import uuid

# Helper for UUID primary keys, compatible with SQLite for testing
# In a production PostgreSQL environment, PG_UUID would be used directly.
def UUID_PRIMARY_KEY():
    return Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

class Category(Base):
    __tablename__ = "categories"

    category_id = UUID_PRIMARY_KEY()
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    preseeded_mappings = relationship("PreseededMapping", back_populates="category")
    custom_mappings = relationship("CustomMapping", back_populates="category")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")

class PreseededMapping(Base):
    __tablename__ = "preseeded_mappings"

    mapping_id = UUID_PRIMARY_KEY()
    merchant_keyword = Column(String, unique=True, index=True, nullable=False)
    category_id = Column(String, ForeignKey("categories.category_id"), nullable=False)

    category = relationship("Category", back_populates="preseeded_mappings")

class CustomMapping(Base):
    __tablename__ = "custom_mappings"

    mapping_id = UUID_PRIMARY_KEY()
    user_id = Column(String, index=True, nullable=False) # Assuming user_id is a string UUID from an external User Service
    merchant_keyword = Column(String, nullable=False)
    category_id = Column(String, ForeignKey("categories.category_id"), nullable=False)
    precedence = Column(Integer, default=1, nullable=False) # 1 for custom, 0 for pre-seeded (though custom always takes precedence)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="custom_mappings")

    __table_args__ = (
        UniqueConstraint("user_id", "merchant_keyword", name="_user_merchant_uc"),
    )

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = UUID_PRIMARY_KEY()
    user_id = Column(String, index=True, nullable=False)
    merchant_name = Column(String, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    raw_description = Column(String, nullable=True)
    categorized_category_id = Column(String, ForeignKey("categories.category_id"), nullable=True)
    categorization_timestamp = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="PENDING", nullable=False)

    category = relationship("Category", back_populates="transactions")

class Budget(Base):
    __tablename__ = "budgets"

    budget_id = UUID_PRIMARY_KEY()
    user_id = Column(String, index=True, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    category_id = Column(String, ForeignKey("categories.category_id"), nullable=False)
    total_spent = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="budgets")

    __table_args__ = (
        UniqueConstraint("user_id", "month", "year", "category_id", name="_user_month_year_category_uc"),
    )
