from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.models import Frequency, RecurringPaymentStatus, TransactionType, TransactionStatus, NotificationType, NotificationStatus

class UserBase(BaseModel):
    email: str
    account_id: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class RecurringPaymentBase(BaseModel):
    biller_name: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    currency: str = Field("USD", min_length=1)
    start_date: datetime
    frequency: Frequency

class RecurringPaymentCreate(RecurringPaymentBase):
    user_id: int

class RecurringPaymentUpdate(BaseModel):
    biller_name: Optional[str] = Field(None, min_length=1)
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=1)
    start_date: Optional[datetime] = None
    frequency: Optional[Frequency] = None
    status: Optional[RecurringPaymentStatus] = None

class RecurringPayment(RecurringPaymentBase):
    id: int
    user_id: int
    next_payment_date: datetime
    status: RecurringPaymentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class TransactionBase(BaseModel):
    user_id: int
    payment_id: Optional[int] = None
    type: TransactionType
    amount: float
    currency: str
    transaction_date: datetime
    status: TransactionStatus
    tag: Optional[str] = None
    description: Optional[str] = None
    external_reference_id: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class NotificationBase(BaseModel):
    user_id: int
    type: NotificationType
    message: str
    timestamp: datetime
    status: NotificationStatus
    related_transaction_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int

    model_config = {"from_attributes": True}
