from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import datetime

from app.db.database import Base

class Frequency(enum.Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class RecurringPaymentStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"

class TransactionType(enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class TransactionStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"

class NotificationType(enum.Enum):
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"

class NotificationStatus(enum.Enum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    account_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    recurring_payments = relationship("RecurringPayment", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class RecurringPayment(Base):
    __tablename__ = "recurring_payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    biller_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    start_date = Column(DateTime(timezone=True), nullable=False)
    frequency = Column(Enum(Frequency), nullable=False)
    next_payment_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(RecurringPaymentStatus), nullable=False, default=RecurringPaymentStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="recurring_payments")
    transactions = relationship("Transaction", back_populates="recurring_payment")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recurring_payment_id = Column(Integer, ForeignKey("recurring_payments.id"), nullable=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(TransactionStatus), nullable=False)
    tag = Column(String, nullable=True)
    description = Column(String, nullable=True)
    external_reference_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="transactions")
    recurring_payment = relationship("RecurringPayment", back_populates="transactions")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(NotificationStatus), nullable=False, default=NotificationStatus.SENT)
    related_transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)

    user = relationship("User", back_populates="notifications")
    related_transaction = relationship("Transaction")
