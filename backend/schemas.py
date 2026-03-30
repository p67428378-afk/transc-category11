from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CustomMappingBase(BaseModel):
    merchant_keyword: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)

class CustomMappingCreate(CustomMappingBase):
    pass

class CustomMappingUpdate(CustomMappingBase):
    pass

class CustomMappingInDB(CustomMappingBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None # Make updated_at optional

    model_config = ConfigDict(from_attributes=True)

class PreseededMappingBase(BaseModel):
    merchant_keyword: str
    category: str
    priority: int = 0

class PreseededMappingInDB(PreseededMappingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class TransactionBase(BaseModel):
    user_id: str
    merchant_name: str
    amount: float
    transaction_date: datetime
    raw_description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionInDB(TransactionBase):
    id: int
    assigned_category: str = "Uncategorized"
    categorization_timestamp: Optional[datetime] = None
    categorization_rule_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class BudgetCategoryBase(BaseModel):
    user_id: str
    month: int
    year: int
    category: str
    budgeted_amount: float
    spent_amount: float = 0.0

class BudgetCategoryInDB(BudgetCategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
