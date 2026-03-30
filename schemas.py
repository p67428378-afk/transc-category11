from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PreseededMappingBase(BaseModel):
    merchant_keyword: str
    category: str
    priority: int = 0

class PreseededMappingCreate(PreseededMappingBase):
    pass

class PreseededMappingResponse(PreseededMappingBase):
    preseeded_mapping_id: str

    class Config:
        from_attributes = True

class CustomMappingBase(BaseModel):
    merchant_keyword: str
    category: str

class CustomMappingCreate(CustomMappingBase):
    pass

class CustomMappingUpdate(BaseModel):
    merchant_keyword: Optional[str] = None
    category: Optional[str] = None

class CustomMappingResponse(CustomMappingBase):
    custom_mapping_id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    merchant_name: str
    amount: int
    transaction_date: datetime
    raw_description: Optional[str] = None

class TransactionCreate(TransactionBase):
    user_id: str

class TransactionResponse(TransactionBase):
    transaction_id: str
    user_id: str
    assigned_category: str = "Uncategorized"
    categorization_timestamp: Optional[datetime] = None
    categorization_rule_id: Optional[str] = None

    class Config:
        from_attributes = True

class BudgetCategoryBase(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000)
    category: str
    budgeted_amount: int = Field(..., ge=0)
    spent_amount: int = Field(..., ge=0)

class BudgetCategoryResponse(BudgetCategoryBase):
    budget_id: str
    user_id: str

    class Config:
        from_attributes = True
