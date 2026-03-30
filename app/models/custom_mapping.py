from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base # Import Base from app.database

class CustomMapping(Base):
    __tablename__ = "custom_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Assuming user_id is an integer for now
    merchant_keyword = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Add a unique constraint for user_id and merchant_keyword
    __table_args__ = (
        UniqueConstraint('user_id', 'merchant_keyword', name='_user_merchant_uc'),
    )
