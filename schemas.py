from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

# Base Schema for Category
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

# Schema for creating a Category
class CategoryCreate(CategoryBase):
    pass

# Schema for updating a Category
class CategoryUpdate(CategoryBase):
    pass

# Schema for a Category response (includes ID)
class CategoryResponse(CategoryBase):
    category_id: str

    model_config = ConfigDict(from_attributes=True)

# Base Schema for PreseededMapping
class PreseededMappingBase(BaseModel):
    merchant_keyword: str = Field(..., min_length=1, max_length=255)
    category_id: str

# Schema for creating a PreseededMapping
class PreseededMappingCreate(PreseededMappingBase):
    pass

# Schema for a PreseededMapping response (includes ID)
class PreseededMappingResponse(PreseededMappingBase):
    mapping_id: str

    model_config = ConfigDict(from_attributes=True)

# Base Schema for CustomMapping
class CustomMappingBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    merchant_keyword: str = Field(..., min_length=1, max_length=255)
    category_id: str

# Schema for creating a CustomMapping
class CustomMappingCreate(CustomMappingBase):
    pass

# Schema for updating a CustomMapping
class CustomMappingUpdate(BaseModel):
    merchant_keyword: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[str] = None

# Schema for a CustomMapping response (includes ID and timestamps)
class CustomMappingResponse(CustomMappingBase):
    mapping_id: str
    precedence: int
    created_at: datetime
    updated_at: Optional[datetime] = None # Made updated_at optional

    model_config = ConfigDict(from_attributes=True)

# Base Schema for Transaction
class TransactionBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    merchant_name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    transaction_date: datetime
    raw_description: Optional[str] = Field(None, max_length=1000)

# Schema for creating a Transaction
class TransactionCreate(TransactionBase):
    pass

# Schema for a Transaction response (includes ID and categorization info)
class TransactionResponse(TransactionBase):
    transaction_id: str
    categorized_category_id: Optional[str] = None
    categorization_timestamp: Optional[datetime] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

# Base Schema for Budget
class BudgetBase(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000)
    category_id: str
    total_spent: float = Field(..., ge=0)

# Schema for creating/updating a Budget
class BudgetCreateUpdate(BudgetBase):
    pass

# Schema for a Budget response (includes ID and last updated)
class BudgetResponse(BudgetBase):
    budget_id: str
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)
