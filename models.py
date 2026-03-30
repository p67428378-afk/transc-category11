import uuid
from sqlalchemy import Column, Float, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PolicyHolder(Base):
    __tablename__ = "policy_holders"

    policyHolderId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    dateOfBirth = Column(Date)
    address = Column(String)
    contactInfo = Column(String)
    ncbYears = Column(Integer, default=0)

    policies = relationship("Policy", back_populates="policyHolder")

class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicleId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policyId = Column(String, ForeignKey("policies.policyId"))
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    vehicleType = Column(String)
    vehicleMultiplier = Column(Float)

    policy = relationship("Policy", back_populates="vehicle")

class Policy(Base):
    __tablename__ = "policies"

    policyId = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policyHolderId = Column(String, ForeignKey("policy_holders.policyHolderId"))
    startDate = Column(Date)
    endDate = Column(Date)
    basePremium = Column(Float)
    calculatedPremium = Column(Float)
    ncbDiscountApplied = Column(Float)
    status = Column(String)

    policyHolder = relationship("PolicyHolder", back_populates="policies")
    vehicle = relationship("Vehicle", uselist=False, back_populates="policy")

class NCBTier(Base):
    __tablename__ = "ncb_tiers"

    ncbYears = Column(Integer, primary_key=True)
    discountPercentage = Column(Float)
