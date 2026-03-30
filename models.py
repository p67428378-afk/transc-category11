from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid

class Policy(Base):
    __tablename__ = "policies"

    policy_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    vehicle_type = Column(String, index=True)
    ncb_years = Column(Integer)
    base_premium = Column(Float)
    ncb_discount_percentage = Column(Float)
    vehicle_multiplier = Column(Float)
    final_premium = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
